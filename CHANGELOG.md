# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [3.2.0](https://gitlab.com/henn1001/qsdl/compare/v3.1.0...v3.2.0) (2023-09-18)


### Features

* **core:** introduce a new date-time scalar type that supports the old date type ([bfb8fb7](https://gitlab.com/henn1001/qsdl/commit/bfb8fb7f393ea3e485fc0b6189876e20f6d09b54))
* **spring:** add a spring-force-generate directive to force generation of unused base types ([57a3a25](https://gitlab.com/henn1001/qsdl/commit/57a3a255edc9ca22184de0b007babb35566747d6))
* **spring:** add new parameter 'base_package' for specifying the package location. ([f2dfff1](https://gitlab.com/henn1001/qsdl/commit/f2dfff15e3af0f9988637df46d1b971c70737bc0))
* **spring:** add Override to all controllers for better alignment with the interface ([dedbbb0](https://gitlab.com/henn1001/qsdl/commit/dedbbb0e16f28b13a4d844bd9e22f81cb3921794))
* **spring:** add transactional to all modifying service layer methods ([e96a18e](https://gitlab.com/henn1001/qsdl/commit/e96a18efd74b8462aa51523111869313adba8767))
* user is informed that body parameters are not allowed for delete operations ([6db6821](https://gitlab.com/henn1001/qsdl/commit/6db682102cea14f7dc475957868c2e939d4c6fc4))


### Bug Fixes

* **core:** allow server path to start other paths than /api ([1851b1b](https://gitlab.com/henn1001/qsdl/commit/1851b1bcc0fcd6683f4b71ae5b2f254f2802e068))
* **core:** prevent field name duplications ([5b0a757](https://gitlab.com/henn1001/qsdl/commit/5b0a757c7301be8af8b604125bec29b9410983c9))
* **openapi:** resolve compatibility issue with readOnly and writeOnly refs ([43b36a4](https://gitlab.com/henn1001/qsdl/commit/43b36a400079d03a8a5ef41f89fa69dd87873345))
* **openapi:** sort operations by path to prevent a wrong path assignment - while qsdl does not care about the order of the paths, openapi does ([326f4dd](https://gitlab.com/henn1001/qsdl/commit/326f4dd4924e1df6fa617b4824b682b1b6c49ac4))
* **openapi:** wrap truthy/falsy yaml enum values into quotes for yaml 1.1 compatibility ([a189937](https://gitlab.com/henn1001/qsdl/commit/a189937c4afc993cd1099c2af73006c1da4b34b9))
* resolved more issues in multiline comment padding ([0c9f970](https://gitlab.com/henn1001/qsdl/commit/0c9f970c981b2ba8927f8324712476249f3da81a))
* **spring:** remove additional curly brace for inheritDoc within controllers ([01e72b3](https://gitlab.com/henn1001/qsdl/commit/01e72b342105d979e2f9d73d2c499f10d083e6d4))
* **spring:** resolve issue when generating operations with request bodies with exactly one scalar/enum value ([13ce644](https://gitlab.com/henn1001/qsdl/commit/13ce644de89d7777fe80cb57dd9bad2c7ed5923e))

## [3.1.0](https://gitlab.com/henn1001/qsdl/compare/v3.0.0...v3.1.0) (2022-06-08)


### Features

* properly handle and indent multi-line comments - utilize custom api comments in spring ([4b2505b](https://gitlab.com/henn1001/qsdl/commit/4b2505b4489d4722e7deecd710b015d4d196ef62))
* **spring:** database mode now generates only the raw class without any relations ([1f18600](https://gitlab.com/henn1001/qsdl/commit/1f1860000fac08056ba19e62bb96e15ccf7dea20))

## [3.0.0](https://gitlab.com/henn1001/qsdl/compare/v2.7.0...v3.0.0) (2022-06-05)


### ⚠ BREAKING CHANGES

* **garammar:** extend api is now all lowercase to make it more consistent with the rest of the language
* **garammar:** remove the 'value: ' section from all directives

### Features

* add directives to scalars to support custom type conversions for openapi and spring ([e17b32f](https://gitlab.com/henn1001/qsdl/commit/e17b32f826bdc46292c093c61f15a4cc88c798b1))
* **core:** add --print_version flag to cli for creating a qsdl version file ([14b54f6](https://gitlab.com/henn1001/qsdl/commit/14b54f664648936f23d8902f45c808ef4d4a2825))
* **core:** replace inflect library for pluralization as it can have unwanted side-effects with a simply "s" append method ([12ac68d](https://gitlab.com/henn1001/qsdl/commit/12ac68d916091ce43b93c2abe1605d5bdcdefe33))
* **grammar:** add a hidden and unique directive that is utilized by openapi and spring respectively ([b269489](https://gitlab.com/henn1001/qsdl/commit/b2694893582d3088a3583c7014e485b82989dfd4))
* **grammar:** add the a '?' marker for custom operation arguments to indicate a query parameter. allows the mixture of body and query parameters ([dad9bba](https://gitlab.com/henn1001/qsdl/commit/dad9bbae85049e51cdf046a79f5aac5c08d3cda9))
* **grammar:** add the a '^' marker for custom operation request headers and a 'headers' directive to add custom operation response headers ([84b281a](https://gitlab.com/henn1001/qsdl/commit/84b281a971bd6a2544470555637f2bb6680159b2))
* **grammar:** allow type definitions without any field. useful for inheritance ([4929ef5](https://gitlab.com/henn1001/qsdl/commit/4929ef582aee4648f620565f4c70e893c701de02))
* introduce minSize and maxSize directive for adding constraints to openapi and spring string,int and longs ([f4492e7](https://gitlab.com/henn1001/qsdl/commit/f4492e752747e64da8aeea4fbdb85b2082f22569))
* **openapi:** change default security header to 'Authorization' ([035ad5e](https://gitlab.com/henn1001/qsdl/commit/035ad5e90b4cd8fa6bb9d03794512f3ed8e7854f))
* **spring:** introduce directive '[@spring-void-input](https://gitlab.com/spring-void-input)' to prevent argument generation for custom operations ([afe6eb2](https://gitlab.com/henn1001/qsdl/commit/afe6eb2b5cfa72adc005da0aa1ffa18f08329c56))
* **spring:** provide a context object for the service layer to access request specific information ([73abeaa](https://gitlab.com/henn1001/qsdl/commit/73abeaa4888c5a0054fe500bb1549335c2df823f))
* **spring:** remove service-test generation when hibernate is disabled ([8b2aa6a](https://gitlab.com/henn1001/qsdl/commit/8b2aa6a1e2b38f6f3af3649fd7163f282dd68573))
* **spring:** remove unneeded annotations from a controller and improve produces/consumes logic ([08a020a](https://gitlab.com/henn1001/qsdl/commit/08a020a5c20c7ce08ddd8a4476b1d965d19a8624))


### Bug Fixes

* **core:** prevent duplicated fields when using multiple extends ([3a2f8e4](https://gitlab.com/henn1001/qsdl/commit/3a2f8e4481be18db6b46d907a1fbb510ae59066b))
* **spring:** align test data generation with default value limits for integers ([92156a0](https://gitlab.com/henn1001/qsdl/commit/92156a08556684aa8418163b74a0c306460a4e06))
* **spring:** embedding the same base type multiple times should not create conflicts in the join-column name ([5e3e292](https://gitlab.com/henn1001/qsdl/commit/5e3e2923f8b89e0bfebca9812a5374fc76b99d18))
* **spring:** resolve issue with accessing the model of querydsl predicates ([bb70821](https://gitlab.com/henn1001/qsdl/commit/bb7082145ae1172c39176c8005120cb6b92e729e))
* **spring:** resolve issue with qsdl-ignore not fully working when the cwd is somewhere else ([48c2702](https://gitlab.com/henn1001/qsdl/commit/48c27023e075c65ecc36576fbf961dbcf226d5c6))
* **spring:** service_layer parameter generation was not working correctly when using path and query parameters, join_column name for nested base types were wrong, using the directive 'spring-void-input' should generate path parameters ([20beda3](https://gitlab.com/henn1001/qsdl/commit/20beda3a7419efc43cf585f6a40ad9620ed4d7b3))


* **garammar:** extend api is now all lowercase to make it more consistent with the rest of the language ([eaf2ea3](https://gitlab.com/henn1001/qsdl/commit/eaf2ea3a3c4d9839b88791365b98972cb45a92fe))
* **garammar:** remove the 'value: ' section from all directives ([40f0789](https://gitlab.com/henn1001/qsdl/commit/40f07895b74a90875b6d987560c21ca0643f3f47))

## [2.7.0](https://gitlab.com/henn1001/qsdl/compare/v2.6.1...v2.7.0) (2022-05-28)


### Features

* **core:** add feature that allows to split domain model files ([77ee258](https://gitlab.com/henn1001/qsdl/commit/77ee2588d3efbafe754080d51109b8f01aeb697f))
* **core:** introduce new generate directive to control the crud generation ([da16e35](https://gitlab.com/henn1001/qsdl/commit/da16e357dc42c3ec2a9ce2d73040ed301a7c608e))
* **core:** introduce new pagination,produces and consumes directive ([c63a512](https://gitlab.com/henn1001/qsdl/commit/c63a5125f35a4818dcd8d51af3d90e3ba07571c7))
* **spring:** add directive [@controller](https://gitlab.com/controller) to overwrite the name for controllers ([1f41e9a](https://gitlab.com/henn1001/qsdl/commit/1f41e9a928754e7b6ccb11d8f3d7d5bfa5092f4e))
* **spring:** custom operations will no longer generate a DefaultService ([273a1ee](https://gitlab.com/henn1001/qsdl/commit/273a1ee8db1b83ff72b3361dc1219128824e1084))
* **spring:** draft for customizable package structure ([9e41bcf](https://gitlab.com/henn1001/qsdl/commit/9e41bcfde7776c2833d07c16269f96d52212f7aa))
* **spring:** introduce a controller interface to allow for more flexible implementation ([77fcaee](https://gitlab.com/henn1001/qsdl/commit/77fcaeedb7b42c2d02eecb676c02da48baeecfe4))
* **spring:** only persist nested base types ([ef189ae](https://gitlab.com/henn1001/qsdl/commit/ef189ae62255085eeb30bd5f8db3411502348540))
* **spring:** simplify service generation logic and improve parent queries for string identifier ([1dfb3ff](https://gitlab.com/henn1001/qsdl/commit/1dfb3ffa6a166bb6c3a2ac53a4a12ce966ca9460))
* **spring:** support for uuid  identifiers by exposing uid as id ([a9ee2e7](https://gitlab.com/henn1001/qsdl/commit/a9ee2e7f6dc2baa73a36e18e10b1d332a12c980c))
* **spring:** update spring-boot version and other various fixes ([e461ca3](https://gitlab.com/henn1001/qsdl/commit/e461ca3fa3ba6b8b8b74bb49ca5f8fc52ac88f4a))


### Bug Fixes

* **core:** allow comments in enums ([ec9da3d](https://gitlab.com/henn1001/qsdl/commit/ec9da3d32e45b08426862898fef79a274930d186))
* **openapi:** correct typo for ref pagination parameter ([1f04a98](https://gitlab.com/henn1001/qsdl/commit/1f04a9878948196a57fe7db9bbb2efc60fe1f0a8))
* **spring:** re-enable nested bean validation because binder was in wrong config class ([dbf543b](https://gitlab.com/henn1001/qsdl/commit/dbf543b3446a9255dd8b5e4fbe2dc439a7087906))
* **spring:** resolve issue in testcase for whenCountByXY_thenUseQuerie ([9893e7a](https://gitlab.com/henn1001/qsdl/commit/9893e7a0c7aab4038ee30cc4f9bb4d11f49c190a))
* **spring:** resolve issue in testcase for whenRemoveXFromY_thenOk ([041ec44](https://gitlab.com/henn1001/qsdl/commit/041ec44f493a5a927cea8f627524fba45ea5877d))
* **spring:** resolve issues with encapsulation flag generating erroneous code ([9d4f8e5](https://gitlab.com/henn1001/qsdl/commit/9d4f8e50b07df02e861e74249f2ab99a5eaa465c))
* **spring:** resolve issues with missing objectnode import when using the controller directive ([3663f1c](https://gitlab.com/henn1001/qsdl/commit/3663f1c9241d98b93ffafdc80aa820340dccb6f9))

### [2.6.1](https://gitlab.com/henn1001/qsdl/compare/v2.6.0...v2.6.1) (2021-10-29)


### Bug Fixes

* **core:** resolve python 3.9 compatibility issue by moving to inquirer ([48e3165](https://gitlab.com/henn1001/qsdl/commit/48e31659f1430547b6d0aed090a8df2b4060dcc4))
* **spring:** resolve issue missing error response for invalid aggregation requests ([783a700](https://gitlab.com/henn1001/qsdl/commit/783a70095f601fa7933f6dee0430b7b6a055dd42))

## [2.6.0](https://gitlab.com/henn1001/qsdl/compare/v2.5.0...v2.6.0) (2021-10-28)


### Features

* **spring:** add flyway for db migration and versioning ([d189ecc](https://gitlab.com/henn1001/qsdl/commit/d189ecc53d228e506d5ce22b00cf705cdd335afb))
* **spring:** introduce profiles - switch from h2 to hsqldb - add postgresql support and docker-compose example ([1d57af3](https://gitlab.com/henn1001/qsdl/commit/1d57af3c341e0841b2b9939baa10d3e42220b35d))
* **spring:** introduce querydsl - update and remove old logic and fix tests ([62a635b](https://gitlab.com/henn1001/qsdl/commit/62a635b8163a6040f4c9ba30b666f0d858af5b94))
* **spring:** introduce querydsl for more typesafe querying ([c5cbea1](https://gitlab.com/henn1001/qsdl/commit/c5cbea18f7e2f15f4e584c19396cb94237170d64))


### Bug Fixes

* **openapi:** add missing cursor parameters to types without query parameters and utilize a more generic query parameter with explode ([b2f8d07](https://gitlab.com/henn1001/qsdl/commit/b2f8d07300e76c9d3a212db3e6b9520aec49e522))
* **openapi:** resolve issue with custom operations query parameters introduced in b2f8d073 ([387e7d5](https://gitlab.com/henn1001/qsdl/commit/387e7d52f1f2de03f79b459de15e87aac395d182))
* **spring:** add datetimeformat information for querydsl and resolve clob compatibility with postgres ([bd005c7](https://gitlab.com/henn1001/qsdl/commit/bd005c718cf33f304962eb920b7e06ba39988d9d))

## [2.5.0](https://gitlab.com/henn1001/qsdl/compare/v2.4.0...v2.5.0) (2021-10-17)


### Features

* add global logger module ([b0d687e](https://gitlab.com/henn1001/qsdl/commit/b0d687e43f87949780aa9178a61020ef007b99b7))
* **spring:** bump version for spring to 2.5.5 and java to 17 ([1eaa87f](https://gitlab.com/henn1001/qsdl/commit/1eaa87fc0c70c4649206bf50f7af4d97470884b8))
* **spring:** prevent generation of unused entities ([38a9b97](https://gitlab.com/henn1001/qsdl/commit/38a9b976c50ae9884810a50473d707dbc9c9051b))
* **spring:** repository tests now consider nested objects ([f4cb566](https://gitlab.com/henn1001/qsdl/commit/f4cb56650e7294200992b5e513fff54b6df6eb1e))
* **spring:** rework and improve repository tests by changing the ownerside for aggregations ([2b7aa13](https://gitlab.com/henn1001/qsdl/commit/2b7aa13b2914394136670b7a42f3c0355339ea91))


### Bug Fixes

* prevent non-array compositions ([6b0485c](https://gitlab.com/henn1001/qsdl/commit/6b0485c87770bf711fae27957f3ae51bc1641184))
* **spring:** resolve issue with writing a "null" string into the database instead of null for objects ([746804d](https://gitlab.com/henn1001/qsdl/commit/746804dbc0fba367187cf55fb046cb252e0d8c60))
* **spring:** resolve issues with nested base & objects by switching from elementcollection to OneToX ([2abd45a](https://gitlab.com/henn1001/qsdl/commit/2abd45a6838f7de15f0124e3aefaadc67c23e4c3))

## [2.4.0](https://gitlab.com/henn1001/qsdl/compare/v2.3.0...v2.4.0) (2021-09-23)


### Features

* add server path rules and a sane default value which connects to the spring generator ([6af2481](https://gitlab.com/henn1001/qsdl/commit/6af2481d43d628ca431ef289033cdd0667d2f991))
* prevent argument name clashes for operations ([0c61d80](https://gitlab.com/henn1001/qsdl/commit/0c61d802912d2a5443c2978089ecdcc8cc60f45e))
* **spring:** prepend an underscore to the internal uuid and version field for entities ([682db0f](https://gitlab.com/henn1001/qsdl/commit/682db0fa6a6fc19ebc11656823bb9e36e90acb86))
* **spring:** use lombok for logging ([7c52ffb](https://gitlab.com/henn1001/qsdl/commit/7c52ffb8376abb7a4188c18be65b7e6f3138b7b4))
* **spring:** utilize lombok for generating getter/setters and add a flag to config to enable this ([76be7df](https://gitlab.com/henn1001/qsdl/commit/76be7dfe231f2b5152fae4b512225af58baba4a7))


### Bug Fixes

* **spring:** resolve issue with delete exceptions wrongly marked as entity not found ([273ba68](https://gitlab.com/henn1001/qsdl/commit/273ba68e59271eaaeeeaf8524ec5d30b919141df))
* **spring:** resolve issue with failed payload test when object has no required fields ([a2f4a98](https://gitlab.com/henn1001/qsdl/commit/a2f4a980ba5476ed502ce150078361fb95799c50))

## [2.3.0](https://gitlab.com/henn1001/qsdl/compare/v2.2.0...v2.3.0) (2021-09-12)


### Features

* **grammar:** remove the nested directive to have a clear separation between relations and nested objects ([6a772e2](https://gitlab.com/henn1001/qsdl/commit/6a772e202ed0e5a3b65984a29ecc021c912108f2))
* **spring:** added repository test generation ([cd31edb](https://gitlab.com/henn1001/qsdl/commit/cd31edb44f97402116e1f35136aeb9a4326cdf47))
* **spring:** added test generation for controllers and services ([69913d1](https://gitlab.com/henn1001/qsdl/commit/69913d123596db20046b9c4c3e64eeb442597ccf))
* **spring:** include relations in the encapsulation parameter ([72195f2](https://gitlab.com/henn1001/qsdl/commit/72195f28de853e8126d5dce07be9cfacd0d4a76b))
* optimize count request for compositions and aggregations ([57aa44d](https://gitlab.com/henn1001/qsdl/commit/57aa44d8b1f52a236e0a4cddf64f1d96cd312ac5))


### Bug Fixes

* **grammar:** allow use of hypens ([fa1eb11](https://gitlab.com/henn1001/qsdl/commit/fa1eb11ab7d08a3b0152f5a48b6f5502bb64a9af))
* **spring:** resolve a relation parent finding issue ([22cca3b](https://gitlab.com/henn1001/qsdl/commit/22cca3bf4eabfdc77cc635b028f85b78796098ef))
* **spring:** resolve issue regarding adding/removing aggregations with public fields ([8eb3fcd](https://gitlab.com/henn1001/qsdl/commit/8eb3fcdc185f2225471053937a239b96bf6334c8))
* **spring:** resolve issues with nested bases and objects ([22109f4](https://gitlab.com/henn1001/qsdl/commit/22109f4a0d1906adbb6aad743e86e9750fcadf2f))

## [2.2.0](https://gitlab.com/henn1001/qsdl/compare/v2.1.0...v2.2.0) (2021-07-18)


### Features

* **core:** add various validation checks and rules to field directive usage ([37c3909](https://gitlab.com/henn1001/qsdl/commit/37c390911cb0d9ebc089305f9157ad6804cf8d91))
* **spring:** add internal flag for public field access ([8ba74e0](https://gitlab.com/henn1001/qsdl/commit/8ba74e0894f996acfe8da8a026a9b6aa248383c6))
* **spring:** added query parameter generation ([04fd528](https://gitlab.com/henn1001/qsdl/commit/04fd5285acd7cce1ffbe611863a7d20905e18aab))
* **spring:** bump to java 16 and springboot 2.5.2 ([884ed11](https://gitlab.com/henn1001/qsdl/commit/884ed11f6ed75e97e52b27eff5d17922bd69c6fe))
* **spring:** switch to ObjectNode for json objects ([cebe117](https://gitlab.com/henn1001/qsdl/commit/cebe117f99c1efdf39d06a107d2b9a373600af14))
* **spring:** utilize text blocks for sql statements ([1a8c3fb](https://gitlab.com/henn1001/qsdl/commit/1a8c3fb39936c84bc7dbb860147481e0931c04b7))
* removed the internal scalar ID in favor of assigning a id to all domain objects by default ([e04e89f](https://gitlab.com/henn1001/qsdl/commit/e04e89fdee68b57cb52e0f57ef8d81a5c8ac4780))
* revert usage of object extensions "allof" for openapi ([fac7136](https://gitlab.com/henn1001/qsdl/commit/fac713605dcc216f972df49f7b68d49dd8ff9547))


### Bug Fixes

* switch namespace of aggregation to parent ([5eebea1](https://gitlab.com/henn1001/qsdl/commit/5eebea150cc9c6fe00e16de56b288a0bb7747429))
* **spring:** prevent unnecessary count queries on getall requests ([42a3d1b](https://gitlab.com/henn1001/qsdl/commit/42a3d1b24056193bcf7d3aaa6c63629a7d9240ec))
* **spring:** resolve issue with nested base-types ([d020146](https://gitlab.com/henn1001/qsdl/commit/d020146c5c5a71e4bfb22e14cf2f942471275f20))

## [2.1.0](https://gitlab.com/henn1001/qsdl/compare/v2.0.0...v2.1.0) (2021-06-26)


### Features

* **spring:** final draft for database support - begin optimizing and testing ([713798e](https://gitlab.com/henn1001/qsdl/commit/713798ea4486a3294043191a668b163c685483d0))
* **spring:** fourth draft for database support ([2ea9b14](https://gitlab.com/henn1001/qsdl/commit/2ea9b142516952ea7d489d551cb756fa1b8bc9e5))
* **spring:** introduce abstract class with uuid and version to resolve object identification and introduce optimistic locking ([5fe757a](https://gitlab.com/henn1001/qsdl/commit/5fe757acd436945fd2c510250ccf33d8d4dda157))
* **spring:** second draft for database support ([0a17abd](https://gitlab.com/henn1001/qsdl/commit/0a17abd0e600e6f484bd245532f5e7e0e64f54b6))
* **spring:** third draft for database support ([051c736](https://gitlab.com/henn1001/qsdl/commit/051c73611052ba208c080c1e5c8922a154a853f5))
* added a void generator that does nothing ([31e3775](https://gitlab.com/henn1001/qsdl/commit/31e37750a73f96b29979602d279a96fe2f152aea))
* added minimal logging information ([02b072d](https://gitlab.com/henn1001/qsdl/commit/02b072d0e76b80aa344e3dbddfc06441067482e7))

## [2.0.0](https://gitlab.com/henn1001/qsdl/compare/v1.0.1...v2.0.0) (2021-06-20)


### ⚠ BREAKING CHANGES

* **grammar:** rename implements to extends as this is a more accurate description
* **grammar:** remove marker ( [value!] ) to indicate non-empty lists from language due to niche usage
* major refactoring and cleanup after recent changes for all generators
* switch default id_type to integer
* prepare for openapi 3.1 read/write only ref support
* introduce paging for list responses

### Features

* upgrade python package dependencies ([5992757](https://gitlab.com/henn1001/qsdl/commit/59927572df83d658f6f26eb5ec087fa797c37379))
* **cli:** support for generator specific configuration list options ([ec5faab](https://gitlab.com/henn1001/qsdl/commit/ec5faaba6361ec2f5d2922d8ed724832271569f3))
* **grammar:** remove marker ( [value!] ) to indicate non-empty lists from language due to niche usage ([0ffaf79](https://gitlab.com/henn1001/qsdl/commit/0ffaf79fe9f3613e8a005fac198c7dfd65238e0b))
* **grammar:** rename implements to extends as this is a more accurate description ([b90c853](https://gitlab.com/henn1001/qsdl/commit/b90c853c2520bc05f3fd399987c1b7ba06f8a329))
* **spring:** added beta version for a spring-boot generator ([b74d342](https://gitlab.com/henn1001/qsdl/commit/b74d342ac266bf7d9089cbf58068ce73254f2e6d))
* **spring:** first draft for database support ([30fcdb6](https://gitlab.com/henn1001/qsdl/commit/30fcdb611072f476559394b828a252c31c637976))
* add internal switch to change ID type for openAPI - mark ID attributes as such with custom attributes ([76e2593](https://gitlab.com/henn1001/qsdl/commit/76e2593df93d6a36e2e4eca45039f25bb8dd9308))
* added modular generator logic and user prompt for the cli ([c3c2819](https://gitlab.com/henn1001/qsdl/commit/c3c2819c65660f898078e21b447290caeb916612))
* added patch calls to modify any attributes  as opposed to put to replace a resource ([a0144ea](https://gitlab.com/henn1001/qsdl/commit/a0144ea93f11201af0852fb14669144b6f27ed4f))
* commit srcgen for better change tracking ([c2cb208](https://gitlab.com/henn1001/qsdl/commit/c2cb208b33fdfc491edfb7d08ee9af39d2ae9b92))
* introduce paging for list responses ([c1f0141](https://gitlab.com/henn1001/qsdl/commit/c1f01412b4a4bc2e5de5c2ef6234f5a6df56459a))
* prepare for openapi 3.1 read/write only ref support ([a41bb3f](https://gitlab.com/henn1001/qsdl/commit/a41bb3f862fdcb4546bb0b8d01762dfbb638c667))
* simplify error responses to default ([c4d7864](https://gitlab.com/henn1001/qsdl/commit/c4d7864e6b4388059058859169ea27038e95a322))
* tag auto-generated crud operations ([2a2f49a](https://gitlab.com/henn1001/qsdl/commit/2a2f49ae5aaf8f7c00965783c19b4a780534c10e))
* **OpenApi:** improve default error response ([3b3faf5](https://gitlab.com/henn1001/qsdl/commit/3b3faf515a64630379561bc2924b0c7101c51528))


### Bug Fixes

* added missing usage of object dataclass ([c338962](https://gitlab.com/henn1001/qsdl/commit/c338962960fd2756b05c11028ed45943c63ebf60))
* **OpenApi:** correctly use id_type for field values that are neither nested/aggregated/composed ([8dc04cf](https://gitlab.com/henn1001/qsdl/commit/8dc04cf0dcee6380154cb2e39cce7e1feb9fab24))
* update and add dependencies for upcoming improvements ([acd806b](https://gitlab.com/henn1001/qsdl/commit/acd806b71e588c39460e6a3c02d18b5d3a78b3a8))
* **grammar:** allow usage of numbers in enums ([8a3ff79](https://gitlab.com/henn1001/qsdl/commit/8a3ff79b2426e37b0e06a842e45f30aadb1e9577))
* **OpenApi:** correct read/write-only for enums and added descriptions to parameters ([df16a3c](https://gitlab.com/henn1001/qsdl/commit/df16a3c977b8b461dfc78b5202dbc862d369fb8e))


### Refactoring

* major refactoring and cleanup after recent changes for all generators ([e0cb400](https://gitlab.com/henn1001/qsdl/commit/e0cb4004537ff6c62b67d117a732c3dbb27a1c72))
* switch default id_type to integer ([0a77eba](https://gitlab.com/henn1001/qsdl/commit/0a77ebaf4270989d976357724636e7171cae5011))

## [1.0.1](https://gitlab.com/henn1001/qsdl/compare/v1.0.0...v1.0.1) (2020-12-19)


### Features

* **OpenApi:** single arguments of scalar type "object" for custom operations omits the schema properties ([74a0757](https://gitlab.com/henn1001/qsdl/commit/74a0757bc55c2884dd8bf85cd0270d173a6c9edf))
* add long and double scalar type ([d24ee30](https://gitlab.com/henn1001/qsdl/commit/d24ee30a006284fbdbc1215593f1383168d3d73b))
* add operation sorting by order of input definition ([9614b0f](https://gitlab.com/henn1001/qsdl/commit/9614b0f9c84669608190f99fcdb9055725b00d96))
* allow to enable/disable generators ([b47fc3a](https://gitlab.com/henn1001/qsdl/commit/b47fc3acdf1dc0c0ded20952a40058f1388f18ba))
* convert inline enums into reusable enums ([43f41fe](https://gitlab.com/henn1001/qsdl/commit/43f41fe837a373df218698125253bfafdb810c25))


### Bug Fixes

* **OpenApi:** required attribute in error schema referenced wrong value ([2cc42fb](https://gitlab.com/henn1001/qsdl/commit/2cc42fb76b407416b727f403477ae58ab9e31e72))



## [1.0.0](https://gitlab.com/henn1001/qsdl/compare/v0.1.0...v1.0.0) (2020-09-23)


### Features

* prevent usage of Void for Base and Object ([e605030](https://gitlab.com/henn1001/qsdl/commit/e605030c129f7d480a851a15d77fcb4eaef46ce1))
* **cli:** add version option ([628d070](https://gitlab.com/henn1001/qsdl/commit/628d070582bdf44abb928d706ad57083e54cb24e))
* added missing validators ([83960df](https://gitlab.com/henn1001/qsdl/commit/83960df26b11026f81e55694dba453259127881a))
* implemented cli interface via click ([457b6dd](https://gitlab.com/henn1001/qsdl/commit/457b6dd21e476bf9f7c90bcbdd8d7420d0972434))
* **grammar:** title, description, version and servers are now optional ([dce8043](https://gitlab.com/henn1001/qsdl/commit/dce80430b94612280e7e669405937f66de878ed1))


### Bug Fixes

* **GraphQL:** nested inputs and custom queries and mutations ([f11311b](https://gitlab.com/henn1001/qsdl/commit/f11311bd92d4576fefa6cb213f7d248d423f3156))
* **OpenAPI:** broken definition when no object type was specified ([25923a3](https://gitlab.com/henn1001/qsdl/commit/25923a3252ce1e15de9a41f0e46a542f3666438c))
* fixed bug with custom operation payload parameter types ([452dead](https://gitlab.com/henn1001/qsdl/commit/452dead0a3f3e52bf45b24f4813baaf4721a21b0))
* **OpenAPI:** fixed regression with base type generation ([e82fe8b](https://gitlab.com/henn1001/qsdl/commit/e82fe8b12c9b83cba4e053a0b81d2c3fa122e99c))
* **OpenAPI:** generate base types regardless of usage ([3114280](https://gitlab.com/henn1001/qsdl/commit/3114280126bf5ee307ec0aa67b610ef4f2cb2604))



## [0.1.0](https://gitlab.com/henn1001/qsdl/compare/7e1100ab6b8fe41fdf073b193fca501f635bb666...v0.1.0) (2020-08-07)


### Features

* hello world from QSDL ([7e1100a](https://gitlab.com/henn1001/qsdl/commit/7e1100ab6b8fe41fdf073b193fca501f635bb666))
