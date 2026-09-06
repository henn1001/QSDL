## Verdict

The separation is reasonable:

- `ErrorCode`: stable application code, default message, HTTP status
- `AppException`: throwable used by application code
- `AppError`: serialized HTTP error response

However, the current implementation couples the exception directly to the API response DTO and has a few correctness/security issues.

## Important issues

### 1. Null detail can cause a secondary `NullPointerException`

`AppError` uses:

```java
List.of(detail)
```

`List.of(...)` rejects `null`.

This is especially problematic here:

```java
throw new AppException(ErrorCode.INTERNAL_SERVER_ERROR, e.getMessage());
```

`Exception.getMessage()` is allowed to return `null`. In that case, the error handling code throws another `NullPointerException` while trying to create the original error response.

Normalize null details:

```java
public AppError(String code, String message, Integer status, String detail) {
    this(code, message, status, null, TimeUtil.now(),
            detail == null ? List.of() : List.of(detail));
}
```

Also ensure the list-based constructor never stores `null`:

```java
details = details == null ? List.of() : List.copyOf(details);
```

`List.copyOf` also prevents callers from mutating the response indirectly through the original list.

### 2. Exception causes are discarded

`AppException` has no `cause` constructor. `AppExceptionUtil` therefore loses the original exception:

```java
throw new AppException(ErrorCode.INTERNAL_SERVER_ERROR, e.getMessage());
```

That makes diagnosis harder and loses the exception chain in logs.

Add constructors such as:

```java
public AppException(ErrorCode error, Throwable cause) {
    super(error.message(), cause);
    this.appError = error.toAppError();
}

public AppException(ErrorCode error, String detail, Throwable cause) {
    super(error.message(), cause);
    this.appError = error.toAppError(detail);
}
```

Then use:

```java
throw new AppException(ErrorCode.INTERNAL_SERVER_ERROR, e.getMessage(), e);
```

Also, `AppExceptionUtil.request(...)` should avoid wrapping an existing `AppException`:

```java
catch (AppException e) {
    throw e;
}
catch (Exception e) {
    throw new AppException(ErrorCode.INTERNAL_SERVER_ERROR, null, e);
}
```

### 3. Internal exception messages are exposed to clients

These values are returned as API details:

```java
e.getMessage()
ex.toString()
```

They may contain SQL fragments, database names, file paths, class names, or other implementation details.

For `500` responses, prefer:

- log the full exception server-side, including the cause
- return only a generic public error
- optionally return a correlation/request ID

For example:

```java
AppError appError = ErrorCode.INTERNAL_SERVER_ERROR.toAppError();
```

Validation errors can expose field-level messages, but unexpected exceptions generally should not.

### 4. `AppError` does not enforce its own invariants

The public record allows values such as:

```java
new AppError(null, null, null, null, null, null);
```

Yet `GlobalExceptionHandler` later assumes that `status` is valid:

```java
HttpStatus.valueOf(enrichedError.status())
```

That can fail with a `NullPointerException` or an invalid-status exception.

Either:

- make `code`, `message`, `status`, and `timestamp` non-null, or
- make the handler robust against missing status and define a fallback

If every `ErrorCode` always has a status, this code in `ErrorCode` is unnecessarily permissive:

```java
this.status = Objects.nonNull(status) ? status.value() : null;
```

Prefer fail-fast behavior:

```java
this.status = Objects.requireNonNull(status, "status").value();
```

## Design issue: exception contains the wire DTO

Currently:

```java
AppException -> AppError
```

This means the application exception is coupled to the HTTP response model. It also means the timestamp is created when the exception is constructed, rather than when the response is built.

For a small generated application, this is acceptable. A cleaner separation would be:

```text
ErrorCode
  code
  message
  HttpStatus

AppException
  ErrorCode
  details
  cause

AppError
  serialized response fields

GlobalExceptionHandler
  maps AppException to AppError
```

In that design, `AppException` stores the `ErrorCode` and details:

```java
private final ErrorCode errorCode;
private final List<String> details;
```

The handler then creates the response:

```java
AppError appError = new AppError(
        ex.errorCode().code(),
        ex.errorCode().message(),
        ex.errorCode().status(),
        ex.details());
```

Benefits:

- application code does not depend on the response DTO
- causes are easier to preserve
- response-specific fields such as `path` and `timestamp` are created at the HTTP boundary
- `ErrorCode` no longer needs `toAppError(...)` overloads

## Small simplifications

### `ErrorCode`

The three overloads are convenient but repetitive:

```java
toAppError()
toAppError(String detail)
toAppError(List<String> details)
```

They can be kept as convenience methods, but internally they should delegate to one list-based method.

Also consider naming the enum property `httpStatus` rather than `status`, since `status()` currently returns an `Integer` rather than the Spring `HttpStatus`:

```java
private final HttpStatus httpStatus;

public HttpStatus httpStatus() {
    return httpStatus;
}

public int statusCode() {
    return httpStatus.value();
}
```

### `AppError`

The following are probably redundant:

```java
@JsonProperty(value = "code")
```

The property name already matches the record component name.

The no-argument constructor also permits an invalid error object. Jackson generally supports record canonical constructors, so it may not be required. Verify the generated Jackson configuration before removing it.

`@RecordBuilder` is only justified because `GlobalExceptionHandler` currently uses:

```java
AppErrorBuilder.builder(appError).path(...).build()
```

If this is the only use, a record method such as `withPath(...)` could remove the builder dependency:

```java
public AppError withPath(String path) {
    return new AppError(code, message, status, path, timestamp, details);
}
```

## Error taxonomy

`ENTITY_NOT_FOUND` mapping to HTTP `404` makes sense.

These utility methods currently map everything else to `400`:

- `entityAlreadyAdded`
- `entityNotAttached`

Depending on the API semantics:

- already-added resource is often `409 Conflict`
- missing attachment may be `404 Not Found`
- invalid relationship state may also be `409 Conflict`

Consider adding `CONFLICT` instead of treating all domain failures as `BAD_REQUEST`.

## Recommended direction

I would apply changes in this order:

1. Fix null detail handling.
2. Preserve causes in `AppException`.
3. Stop returning raw unexpected exception messages to clients.
4. Make `details` immutable and non-null.
5. Decide whether `AppException` should store `AppError` or only `ErrorCode` plus details.

The three classes do not need to be collapsed into one. The main improvement is defining a clearer boundary between internal exceptions and the serialized HTTP error model.

Since these files are generated, changes should ultimately be made in the QSDL generator/template rather than only in this generated output.