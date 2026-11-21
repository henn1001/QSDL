package app.api.media;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/** Hand-maintained file storage overlay; callers address files by media metadata, never by paths. */
@Service
public class PetMediaStorageService {
    static final long MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
    private final Path root;

    public PetMediaStorageService(@Value("${pet-media.storage-directory:./storage/pet-media}") String directory)
            throws IOException {
        if (directory == null || directory.isBlank()) {
            throw new IllegalArgumentException("Storage directory must not be blank");
        }
        this.root = Path.of(directory).toAbsolutePath().normalize();
        Files.createDirectories(root);
        if (Files.isSymbolicLink(root) || !Files.isDirectory(root, LinkOption.NOFOLLOW_LINKS)) {
            throw new IllegalArgumentException("Storage directory must be a real directory");
        }
    }

    /** Stores a new file and returns its opaque storage key. */
    public String store(String petId, String filename, InputStream content) throws IOException {
        String safePetId = safeSegment(petId, "pet identifier");
        String safeFilename = safeFilename(filename);
        if (content == null) {
            throw new IllegalArgumentException("Content must not be null");
        }

        Path directory = root.resolve(safePetId);
        Files.createDirectories(directory);
        assertSafeDirectory(directory);
        String key = UUID.randomUUID() + "-" + safeFilename;
        Path target = directory.resolve(key);
        long copied = 0;
        try (var output = Files.newOutputStream(target, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            byte[] buffer = new byte[8192];
            int read;
            while ((read = content.read(buffer)) != -1) {
                copied += read;
                if (copied > MAX_UPLOAD_BYTES) {
                    throw new IOException("Uploaded file exceeds the size limit");
                }
                output.write(buffer, 0, read);
            }
        } catch (IOException | RuntimeException exception) {
            Files.deleteIfExists(target);
            try {
                Files.deleteIfExists(directory);
            } catch (IOException ignored) {
                // Preserve the original upload failure.
            }
            throw exception;
        }
        return safePetId + "/" + key;
    }

    /** Resolves a persisted key after validating every path component. */
    public Path resolve(String storageKey) throws IOException {
        if (storageKey == null || storageKey.isBlank()) {
            throw new IllegalArgumentException("Storage key must not be blank");
        }
        String[] parts = storageKey.split("/", -1);
        if (parts.length != 2) {
            throw new IllegalArgumentException("Invalid storage key");
        }
        String petId = safeSegment(parts[0], "pet identifier");
        String file = safeStorageKey(parts[1]);
        Path directory = root.resolve(petId);
        assertSafeDirectory(directory);
        Path target = directory.resolve(file);
        if (!Files.isRegularFile(target, LinkOption.NOFOLLOW_LINKS) || Files.isSymbolicLink(target)) {
            throw new IOException("Stored media is missing");
        }
        return target;
    }

    private void assertSafeDirectory(Path directory) throws IOException {
        if (Files.isSymbolicLink(directory) || !Files.isDirectory(directory, LinkOption.NOFOLLOW_LINKS)
                || !directory.toRealPath().startsWith(root.toRealPath())) {
            throw new IOException("Invalid storage path");
        }
    }

    private static String safeFilename(String value) {
        if (value == null || value.isBlank() || value.contains("/") || value.contains("\\")) {
            throw new IllegalArgumentException("Invalid filename");
        }
        String name = Path.of(value).getFileName().toString();
        if (!name.equals(value) || name.equals(".") || name.equals("..")
                || !name.matches("[a-zA-Z0-9][a-zA-Z0-9._-]{0,254}")) {
            throw new IllegalArgumentException("Invalid filename");
        }
        return name;
    }

    private static String safeStorageKey(String value) {
        if (value == null || !value.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,383}")) {
            throw new IllegalArgumentException("Invalid storage key");
        }
        return value;
    }

    private static String safeSegment(String value, String label) {
        if (value == null || !value.matches("[A-Za-z0-9_-]{1,128}")) {
            throw new IllegalArgumentException("Invalid " + label);
        }
        return value;
    }
}
