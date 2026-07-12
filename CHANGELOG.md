# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [6.3.1](https://github.com/henn1001/QSDL/compare/v6.3.0...v6.3.1) (2026-05-20)


### Bug Fixes

* **core:** solved issue with consecutive usage of ignore directive ([ca39c88](https://github.com/henn1001/QSDL/commit/ca39c88d9257ce26d5d1275cf552db022add7f07))

## [6.3.0](https://github.com/henn1001/QSDL/compare/v6.2.0...v6.3.0) (2026-03-22)


### Features

* generate named request DTOs for custom write operations ([3c1daef](https://github.com/henn1001/QSDL/commit/3c1daefa0f471aeaaa9f9b3dddba9bfc8e3b29cf))
* **openapi:** align typing with spring generator for crud paginated filter ([51d8d96](https://github.com/henn1001/QSDL/commit/51d8d96461e816db63ba27ffd7abcfb0bd9c12b9))


### Bug Fixes

* resolve issue with transient not beeing correctly handeled when used on nested bases for both postgres and spring generator ([0822d41](https://github.com/henn1001/QSDL/commit/0822d412f063e49c4eca5952bc5b68083ea0e95c))
* **spring:** correctly handle repository filter tests ([1fbf00d](https://github.com/henn1001/QSDL/commit/1fbf00d71939483e051f008afb12d748d28cd868))
* **spring:** jackson value inclusion wrongly pruned empty lists ([b76b0e0](https://github.com/henn1001/QSDL/commit/b76b0e0f877a9634f598ceda851f65fabc6bb448))
* **spring:** remove redundant filter dto wrapping when using base types ([c9eb21a](https://github.com/henn1001/QSDL/commit/c9eb21a19bdd89e7a3cd09b36feee2195d20cd45))

## [6.2.0](https://github.com/henn1001/QSDL/compare/v6.1.0...v6.2.0) (2026-02-03)


### Features

* all new directive queryList - allows for filtering for multiple values ([add1135](https://github.com/henn1001/QSDL/commit/add11351cb8208a5cd4a9c17404b8565183390f7))
* **spring:** dynamicaly resolve used imports and replace star imports ([c7022ad](https://github.com/henn1001/QSDL/commit/c7022adc46b22a286a69f02e232781ce2cb8bb3f))

## [6.1.0](https://github.com/henn1001/QSDL/compare/v6.0.0...v6.1.0) (2026-02-01)


### Features

* **core:** allow usage of 'id' for base type field names but include 'uid' and 'iv' reservation for object type field names ([76917a5](https://github.com/henn1001/QSDL/commit/76917a507cd2faac72168bc080d79ac8f29105dc))
* re-introduce type generation for query parameters ([b0dcd51](https://github.com/henn1001/QSDL/commit/b0dcd515a9aa61bed6a147d617dd7b4f679751ee))
* **spring:** consolidate JsonUtils with jackson3 ([daee2bf](https://github.com/henn1001/QSDL/commit/daee2bf3429ca68b3398e588c8caff4e740c1d6c))
* **spring:** convert CursorPage and AppError into records ([7f6d64f](https://github.com/henn1001/QSDL/commit/7f6d64fc6aa2c1186be820bb628ee905574d6caa))
* **spring:** minor refactor in Enum.hasValue method ([2d500bc](https://github.com/henn1001/QSDL/commit/2d500bc9f9d268c1c5c5d96fed48cd6dbdad0d40))
* **spring:** only split base types into request/response when required ([87cc27f](https://github.com/henn1001/QSDL/commit/87cc27fbab4ef1e7934f2a4a9086e250d2bfeaeb))
* **spring:** remove startup warning about open-in-view ([111194e](https://github.com/henn1001/QSDL/commit/111194eab3f930bb793ab5c495eed9f7c9908a61))


### Bug Fixes

* Filter models now respect [@spring-package](https://gitlab.com/spring-package) and namespace for domain layouts ([094218e](https://github.com/henn1001/QSDL/commit/094218e74bd7df05c863edd7b9b5a6f3736b91d7))

## [6.0.0](https://github.com/henn1001/QSDL/compare/v5.0.0...v6.0.0) (2026-01-19)


### ⚠ BREAKING CHANGES

* **spring:** introduce JSON Merge Patch behavior for patch endpoints
* **core:** removal of PUT from CRUD generation - replaced by JSON Merge Patch support (RFC 7396)
* **spring:** bump generator to spring-boot 4
* **spring:** deprecate use_builder and use_encapsulation
* **spring:** convert DTOs from classes to Java records

### Features

* **core:** removal of PUT from CRUD generation - replaced by JSON Merge Patch support (RFC 7396) ([f18da33](https://github.com/henn1001/QSDL/commit/f18da333ec441a5caecc062554cbff687f7e5c0b))
* split DTO records into separate Request and Response models ([512d945](https://github.com/henn1001/QSDL/commit/512d945b84fdf9f0829f98fc2b03309641f8b32b))
* **spring:** bump generator to spring-boot 4 ([16e7c7d](https://github.com/henn1001/QSDL/commit/16e7c7d628f893c5849a8340a38f1004fe19cc56))
* **spring:** deprecate use_builder and use_encapsulation ([2f08f8a](https://github.com/henn1001/QSDL/commit/2f08f8a24a84e74a2db4bb455a42be56a99c0752))
* **spring:** integrate record-builder for DTO builders ([f5f8ff2](https://github.com/henn1001/QSDL/commit/f5f8ff237eef04b8ba792ca4a2e2dee0108a88a9))
* **spring:** introduce JSON Merge Patch behavior for patch endpoints ([2f2dd86](https://github.com/henn1001/QSDL/commit/2f2dd86c3fe14b032d1aa17bd16600b204cc1c48))
* **spring:** mark reading service methods with readOnly transactional ([36e13b6](https://github.com/henn1001/QSDL/commit/36e13b625dd1d4361029f57497884d8ea16ea35f))
* **spring:** replace deprecated Testcontainers postgres interface with newer variant ([cc8a470](https://github.com/henn1001/QSDL/commit/cc8a4707c8756ebef94169ffbdb30c302a7f267c))
* **spring:** replace unmaintained easyrandom library with instanceio ([14eafbc](https://github.com/henn1001/QSDL/commit/14eafbcd122f7e4a8f0533b323b6b961f3d36b91))


### Bug Fixes

* **core:** resolve broken usage of scalar definitions ([e1da044](https://github.com/henn1001/QSDL/commit/e1da044bc85e6d6a95d24487f5fe77651bd63b02))
* **spring:** resolve mapper issues occuring with more complex scenarios by simplifying the mapstruct interfaces ([789680a](https://github.com/henn1001/QSDL/commit/789680af013831e300a64c82c51ecd768f4c2d86))


* **spring:** convert DTOs from classes to Java records ([9452e70](https://github.com/henn1001/QSDL/commit/9452e70a958c424a480a0fee5e6598b1edecb562))

## [5.0.0](https://github.com/henn1001/QSDL/compare/v4.5.0...v5.0.0) (2026-01-12)


### ⚠ BREAKING CHANGES

* **spring:** adapt to new opaque and postgres schema behavior
* **spring:** added include postgres to spring generator
* **core:** added a new directive override that is now required when redefining extended fields
* **spring:** upgrade to java 25
* switch from poetry to uv

### Features

* add i18n generator ([e31ddc3](https://github.com/henn1001/QSDL/commit/e31ddc3cca142097d362354d252fd6a04639e8f2))
* **core:** added a new directive override that is now required when redefining extended fields ([17583d1](https://github.com/henn1001/QSDL/commit/17583d1c22e32df71c9a4a698b961433fe844b2e))
* **core:** added two new directives, ignore removes a field completely from further generation and transient removes it from database layers ([d2e04a2](https://github.com/henn1001/QSDL/commit/d2e04a2f26251c9e0d02801f0282a2dc2359a46f))
* **core:** allow extending multiple base types at once and added validation that prevents recursion ([0e36ce8](https://github.com/henn1001/QSDL/commit/0e36ce830c6143458abb5aabf71de7b14ff8e825))
* **core:** introduce opaque directive that will introduce breaking changes on database models ([29520f4](https://github.com/henn1001/QSDL/commit/29520f449c085e55206bd56f76dc3b05846d8c57))
* migrated from click to typer ([aa7aee6](https://github.com/henn1001/QSDL/commit/aa7aee68d7f7f31c223a3eb0cb62e9f5436bea1a))
* **postgres:** all new postgres schema generator that integrates into the spring generator ([d153cb8](https://github.com/henn1001/QSDL/commit/d153cb8b5813b0649d736b3814ff3ee31ce82579))
* **spring:** adapt to new opaque and postgres schema behavior ([b69d040](https://github.com/henn1001/QSDL/commit/b69d0400a536f9d9576ede8b7e860d281921c15d))
* **spring:** added include postgres to spring generator ([146e89c](https://github.com/henn1001/QSDL/commit/146e89c6282e62d57edbcc0b51767189cf07998b))
* **spring:** introduce new parameter table_prefix - can be used for mitigating issues with preserved database names ([2827b53](https://github.com/henn1001/QSDL/commit/2827b530abab4a07bae777f5d3c225394ee857ab))
* **spring:** introduce spotless with palantir formatting - folder restructuring and other improvements ([a8d1b80](https://github.com/henn1001/QSDL/commit/a8d1b80affa7b338038ff8d781a25162894d2788))
* **spring:** switch AppProperties from Class to Record ([64dbbf1](https://github.com/henn1001/QSDL/commit/64dbbf186270e967965ef8931e3846c619c26e5f))
* **spring:** upgrade to java 25 ([f970fab](https://github.com/henn1001/QSDL/commit/f970fab2e794c9c53cd2e70db5327074ab069c5b))


### Bug Fixes

* **core:** allow empty base declarations - usefull when extending ([4934e16](https://github.com/henn1001/QSDL/commit/4934e16b2055fcacbdd9edad1671d91bb406d13d))
* re-added pv shortcut to print version ([3a23ed9](https://github.com/henn1001/QSDL/commit/3a23ed9e57798ce8f452ffb032a3d4f15e7eb66c))
* **spring:** do not use min/max annotation for lists of integer or long ([7834ae9](https://github.com/henn1001/QSDL/commit/7834ae914f4c25c566a2b73c4b45c4f3046aac7b))
* **spring:** prevent duplicates in repository and mapper package resolution ([8b5fb5b](https://github.com/henn1001/QSDL/commit/8b5fb5ba848591c842c0499ad8db9a8faf662036))


### build

* switch from poetry to uv ([d28a934](https://github.com/henn1001/QSDL/commit/d28a93435f62b47514687738697bad683d5a5bbc))

## [4.5.0](https://github.com/henn1001/QSDL/compare/v4.4.0...v4.5.0) (2025-08-03)


### Features

* downgrade datatype for cursorpagable limit from long to int ([14728d6](https://github.com/henn1001/QSDL/commit/14728d68692b8a8739103adf41e10aed3f58827a))
* **spring:** allow changing the uid string of db entities ([9335896](https://github.com/henn1001/QSDL/commit/9335896d8fdf7312784dff2a7f489cc42d8c9a0f))
* **spring:** QueryDSL - add interface for EntityManager and JPAQuery to BaseRepository ([2cfb32a](https://github.com/henn1001/QSDL/commit/2cfb32a83c17d9372196be434d140f5654fcabd9))


### Bug Fixes

* **core:** allow enums values as query parameter ([5142086](https://github.com/henn1001/QSDL/commit/5142086d829cddd471f768ed7048a2efb3913c05))
* **spring:** correctly apply regex pattern to lists ([caad1ae](https://github.com/henn1001/QSDL/commit/caad1ae35315af51fb3ff5813ec235df4d770667))
* **spring:** make sure defaults for boolean are correctly handled ([0714192](https://github.com/henn1001/QSDL/commit/071419299cbf7a215751936e70dac97a4194bddc))
* **spring:** resolve an issue with default value for booleans ([36a084a](https://github.com/henn1001/QSDL/commit/36a084a5ffb5baeb1caf7f9c22b74e6890f5b740))

## [4.4.0](https://github.com/henn1001/QSDL/compare/v4.3.0...v4.4.0) (2025-02-03)


### Features

* **spring:** scalar [@spring](https://gitlab.com/spring) anotation - allow defining a seperate type of database entities and regex pattern on api dtos ([44d48c0](https://github.com/henn1001/QSDL/commit/44d48c030c1bf79b8db4d92a0750b8b8eb16ef10))


### Bug Fixes

* **spring:** added missing builder default annotation ([7b5fb66](https://github.com/henn1001/QSDL/commit/7b5fb66a2afc2a710ff277f39f81bf65c731096e))

## [4.3.0](https://github.com/henn1001/QSDL/compare/v4.2.0...v4.3.0) (2024-11-20)


### Features

* **openapi:** removed extra unnecessary query when generating paginated objects due to issues in commonly generated clients ([dc0fbe3](https://github.com/henn1001/QSDL/commit/dc0fbe314ba07b7377be5bc5b5ff02fe13996926))
* **spring:** consolidate DataJapaTest annotations by introducing a abstract class - also adds support for integration test via testcontainers ([6370529](https://github.com/henn1001/QSDL/commit/6370529680f6bbda9d02341327d79d32f81d3fa3))
* **spring:** introduce auditing via hibernate envers ([9833e15](https://github.com/henn1001/QSDL/commit/9833e15146c4ffcb724fdc6d13c12fec9f1a8c56))
* **spring:** introduce builder pattern for dtos ([7e51fd9](https://github.com/henn1001/QSDL/commit/7e51fd925647d35dab9038bd33c7c8b4bade89e6))
* **spring:** introduce JSONAssert ([dfd87d4](https://github.com/henn1001/QSDL/commit/dfd87d4a93b44a039a91320a539b29332dfaea47))
* **spring:** minor class visibility changes ([95e4530](https://github.com/henn1001/QSDL/commit/95e4530661948459745988c8a112ed5b2a5e4030))
* **spring:** seperate utility methods from TestConfig into TestUtils ([af8f55a](https://github.com/henn1001/QSDL/commit/af8f55a0d074d0b67967fc1010574c69c5669a0e))
* **spring:** upgrade to java 21 ([10867f2](https://github.com/henn1001/QSDL/commit/10867f21238c66d73a6d8cceeb8719e9162d0823))
* **spring:** upgrade to spring 3.3 and general refactoring and improvements ([fb3ab9b](https://github.com/henn1001/QSDL/commit/fb3ab9b125188cdc73e1ae5a736ed8b90e0fd7ac))
* **spring:** upgrade to spring 3.3.5 ([ee958f7](https://github.com/henn1001/QSDL/commit/ee958f79ce36d38b81fa22a9841da0d04955e342))
* **spring:** use virtual thread scheduling and other modernizations ([94aa2c9](https://github.com/henn1001/QSDL/commit/94aa2c96f6d54221de2a8c14a992c761f14c5bb8))


### Bug Fixes

* **spring:** add missing import statement for validator whenever service layer generation was involved but no PATCH endpoint declared ([0023776](https://github.com/henn1001/QSDL/commit/002377651a10d3cbaf2ec55cf21dabde7ba3be2a))
* **spring:** default values are now properly generated for dtos and boolean values in general ([1c69b39](https://github.com/henn1001/QSDL/commit/1c69b39cdcbb18129c49538f6d306d5229ac296d))
* **spring:** schema creation still used deprecrated javax settings instead of jakarta ([90b301a](https://github.com/henn1001/QSDL/commit/90b301ade49b16031f2f9209dcf013c7f14f8998))

## [4.2.0](https://github.com/henn1001/QSDL/compare/v4.1.0...v4.2.0) (2024-05-21)


### Features

* **core:** add a new default directive ([c906a9c](https://github.com/henn1001/QSDL/commit/c906a9c11f0c7b7664341bd74554c341c3a8df06))
* **spring:** update spring-boot to v3.1.3 ([8f21860](https://github.com/henn1001/QSDL/commit/8f218609fae5199a7ea00e7193b61ad9df5654d4))
* update openapi to 3.1.0 and adapt the spring and openapi generators accordingly ([cdcb276](https://github.com/henn1001/QSDL/commit/cdcb276ebf1d9e0661216a7d0be5d6b091c440c8))

## [4.1.0](https://github.com/henn1001/QSDL/compare/v4.0.0...v4.1.0) (2023-09-18)


### Features

* openapi - spring - change AppError.code from int to string for more flexibility ([0e012f5](https://github.com/henn1001/QSDL/commit/0e012f5e05962bfcad11410e5ce7e3c18140b01f))
* **spring:** remove @Validated and @Valid from api and controller in favor of calling the validator manually within the controller to offer more flexibility ([466a2d6](https://github.com/henn1001/QSDL/commit/466a2d621fcd4108280f070ecb3560e3a17af9c8))

## [4.0.0](https://github.com/henn1001/QSDL/compare/v3.2.0...v4.0.0) (2023-09-18)


### ⚠ BREAKING CHANGES

* removed graphql generator
* update dependencies and move on to python 3.11 - dropping support for older versions
* promote the spring specific force-generate directive to a core feature. base and enum entities are now omitted by default when not used

### Features

* **core:** allow re-defining inherited fields from super-types ([ed7142a](https://github.com/henn1001/QSDL/commit/ed7142af2edc8f22e69cd8c25cd1bfae02e9fcf3))
* enable color coded logging :) ([5fef64f](https://github.com/henn1001/QSDL/commit/5fef64f4dbd4c77f1248e0e8167f9e77cb044fa4))
* promote the spring specific force-generate directive to a core feature. base and enum entities are now omitted by default when not used ([50358e6](https://github.com/henn1001/QSDL/commit/50358e69bb63546b39ce716bb5ebdd6b630c471e))
* removed graphql generator ([254babc](https://github.com/henn1001/QSDL/commit/254babc23674ffec68652d104e67549f148bf266))
* **spring:** [@spring-package](https://gitlab.com/spring-package) now available for more flexible domain oriented package layouts ([a3917ad](https://github.com/henn1001/QSDL/commit/a3917ad0d0b4d1b707b3e8b975983a77f79317f7))
* **spring:** config - decouple folder_paths from base_package for more flexibility ([b6affbf](https://github.com/henn1001/QSDL/commit/b6affbf654ebc0be7dc249cfde0fe83058f3f1a4))
* **spring:** downgraded AppException to a RuntimeException ([200bb4c](https://github.com/henn1001/QSDL/commit/200bb4c22d63145fab86c6191de6ae33b73a2b1e))
* **spring:** simplify enums ([3e34122](https://github.com/henn1001/QSDL/commit/3e341221123a5080659af9a2bf75c3efa8cd235d))
* **spring:** split dto and entity for hibernate generation ([6ee0a34](https://github.com/henn1001/QSDL/commit/6ee0a3416405ac1af9b50bf1a5e44c37bbdf2818))


### Bug Fixes

* **spring:** add missing objectnode import when using custom scalars for api interfaces ([47c1710](https://github.com/henn1001/QSDL/commit/47c17107c8fe422a5acb11ed485527d3226462b7))
* **spring:** delete operations on uuids should now throw the correct exception by replacing the jpa deleteBy with find & delete ([9cb8a7c](https://github.com/henn1001/QSDL/commit/9cb8a7c96e23c90880c07aa5ccd5b196e3059c4a))


### build

* update dependencies and move on to python 3.11 - dropping support for older versions ([411d99d](https://github.com/henn1001/QSDL/commit/411d99de8f50d9d361535ed27364e1e018c73b89))

## [3.2.0](https://github.com/henn1001/QSDL/compare/v3.1.0...v3.2.0) (2023-09-18)


### Features

* **core:** introduce a new date-time scalar type that supports the old date type ([bfb8fb7](https://github.com/henn1001/QSDL/commit/bfb8fb7f393ea3e485fc0b6189876e20f6d09b54))
* **spring:** add a spring-force-generate directive to force generation of unused base types ([57a3a25](https://github.com/henn1001/QSDL/commit/57a3a255edc9ca22184de0b007babb35566747d6))
* **spring:** add new parameter 'base_package' for specifying the package location. ([f2dfff1](https://github.com/henn1001/QSDL/commit/f2dfff15e3af0f9988637df46d1b971c70737bc0))
* **spring:** add Override to all controllers for better alignment with the interface ([dedbbb0](https://github.com/henn1001/QSDL/commit/dedbbb0e16f28b13a4d844bd9e22f81cb3921794))
* **spring:** add transactional to all modifying service layer methods ([e96a18e](https://github.com/henn1001/QSDL/commit/e96a18efd74b8462aa51523111869313adba8767))
* user is informed that body parameters are not allowed for delete operations ([6db6821](https://github.com/henn1001/QSDL/commit/6db682102cea14f7dc475957868c2e939d4c6fc4))


### Bug Fixes

* **core:** allow server path to start other paths than /api ([1851b1b](https://github.com/henn1001/QSDL/commit/1851b1bcc0fcd6683f4b71ae5b2f254f2802e068))
* **core:** prevent field name duplications ([5b0a757](https://github.com/henn1001/QSDL/commit/5b0a757c7301be8af8b604125bec29b9410983c9))
* **openapi:** resolve compatibility issue with readOnly and writeOnly refs ([43b36a4](https://github.com/henn1001/QSDL/commit/43b36a400079d03a8a5ef41f89fa69dd87873345))
* **openapi:** sort operations by path to prevent a wrong path assignment - while qsdl does not care about the order of the paths, openapi does ([326f4dd](https://github.com/henn1001/QSDL/commit/326f4dd4924e1df6fa617b4824b682b1b6c49ac4))
* **openapi:** wrap truthy/falsy yaml enum values into quotes for yaml 1.1 compatibility ([a189937](https://github.com/henn1001/QSDL/commit/a189937c4afc993cd1099c2af73006c1da4b34b9))
* resolved more issues in multiline comment padding ([0c9f970](https://github.com/henn1001/QSDL/commit/0c9f970c981b2ba8927f8324712476249f3da81a))
* **spring:** remove additional curly brace for inheritDoc within controllers ([01e72b3](https://github.com/henn1001/QSDL/commit/01e72b342105d979e2f9d73d2c499f10d083e6d4))
* **spring:** resolve issue when generating operations with request bodies with exactly one scalar/enum value ([13ce644](https://github.com/henn1001/QSDL/commit/13ce644de89d7777fe80cb57dd9bad2c7ed5923e))

## [3.1.0](https://github.com/henn1001/QSDL/compare/v3.0.0...v3.1.0) (2022-06-08)


### Features

* properly handle and indent multi-line comments - utilize custom api comments in spring ([4b2505b](https://github.com/henn1001/QSDL/commit/4b2505b4489d4722e7deecd710b015d4d196ef62))
* **spring:** database mode now generates only the raw class without any relations ([1f18600](https://github.com/henn1001/QSDL/commit/1f1860000fac08056ba19e62bb96e15ccf7dea20))

## [3.0.0](https://github.com/henn1001/QSDL/compare/v2.7.0...v3.0.0) (2022-06-05)


### ⚠ BREAKING CHANGES

* **garammar:** extend api is now all lowercase to make it more consistent with the rest of the language
* **garammar:** remove the 'value: ' section from all directives

### Features

* add directives to scalars to support custom type conversions for openapi and spring ([e17b32f](https://github.com/henn1001/QSDL/commit/e17b32f826bdc46292c093c61f15a4cc88c798b1))
* **core:** add --print_version flag to cli for creating a qsdl version file ([14b54f6](https://github.com/henn1001/QSDL/commit/14b54f664648936f23d8902f45c808ef4d4a2825))
* **core:** replace inflect library for pluralization as it can have unwanted side-effects with a simply "s" append method ([12ac68d](https://github.com/henn1001/QSDL/commit/12ac68d916091ce43b93c2abe1605d5bdcdefe33))
* **grammar:** add a hidden and unique directive that is utilized by openapi and spring respectively ([b269489](https://github.com/henn1001/QSDL/commit/b2694893582d3088a3583c7014e485b82989dfd4))
* **grammar:** add the a '?' marker for custom operation arguments to indicate a query parameter. allows the mixture of body and query parameters ([dad9bba](https://github.com/henn1001/QSDL/commit/dad9bbae85049e51cdf046a79f5aac5c08d3cda9))
* **grammar:** add the a '^' marker for custom operation request headers and a 'headers' directive to add custom operation response headers ([84b281a](https://github.com/henn1001/QSDL/commit/84b281a971bd6a2544470555637f2bb6680159b2))
* **grammar:** allow type definitions without any field. useful for inheritance ([4929ef5](https://github.com/henn1001/QSDL/commit/4929ef582aee4648f620565f4c70e893c701de02))
* introduce minSize and maxSize directive for adding constraints to openapi and spring string,int and longs ([f4492e7](https://github.com/henn1001/QSDL/commit/f4492e752747e64da8aeea4fbdb85b2082f22569))
* **openapi:** change default security header to 'Authorization' ([035ad5e](https://github.com/henn1001/QSDL/commit/035ad5e90b4cd8fa6bb9d03794512f3ed8e7854f))
* **spring:** introduce directive '[@spring-void-input](https://gitlab.com/spring-void-input)' to prevent argument generation for custom operations ([afe6eb2](https://github.com/henn1001/QSDL/commit/afe6eb2b5cfa72adc005da0aa1ffa18f08329c56))
* **spring:** provide a context object for the service layer to access request specific information ([73abeaa](https://github.com/henn1001/QSDL/commit/73abeaa4888c5a0054fe500bb1549335c2df823f))
* **spring:** remove service-test generation when hibernate is disabled ([8b2aa6a](https://github.com/henn1001/QSDL/commit/8b2aa6a1e2b38f6f3af3649fd7163f282dd68573))
* **spring:** remove unneeded annotations from a controller and improve produces/consumes logic ([08a020a](https://github.com/henn1001/QSDL/commit/08a020a5c20c7ce08ddd8a4476b1d965d19a8624))


### Bug Fixes

* **core:** prevent duplicated fields when using multiple extends ([3a2f8e4](https://github.com/henn1001/QSDL/commit/3a2f8e4481be18db6b46d907a1fbb510ae59066b))
* **spring:** align test data generation with default value limits for integers ([92156a0](https://github.com/henn1001/QSDL/commit/92156a08556684aa8418163b74a0c306460a4e06))
* **spring:** embedding the same base type multiple times should not create conflicts in the join-column name ([5e3e292](https://github.com/henn1001/QSDL/commit/5e3e2923f8b89e0bfebca9812a5374fc76b99d18))
* **spring:** resolve issue with accessing the model of querydsl predicates ([bb70821](https://github.com/henn1001/QSDL/commit/bb7082145ae1172c39176c8005120cb6b92e729e))
* **spring:** resolve issue with qsdl-ignore not fully working when the cwd is somewhere else ([48c2702](https://github.com/henn1001/QSDL/commit/48c27023e075c65ecc36576fbf961dbcf226d5c6))
* **spring:** service_layer parameter generation was not working correctly when using path and query parameters, join_column name for nested base types were wrong, using the directive 'spring-void-input' should generate path parameters ([20beda3](https://github.com/henn1001/QSDL/commit/20beda3a7419efc43cf585f6a40ad9620ed4d7b3))


* **garammar:** extend api is now all lowercase to make it more consistent with the rest of the language ([eaf2ea3](https://github.com/henn1001/QSDL/commit/eaf2ea3a3c4d9839b88791365b98972cb45a92fe))
* **garammar:** remove the 'value: ' section from all directives ([40f0789](https://github.com/henn1001/QSDL/commit/40f07895b74a90875b6d987560c21ca0643f3f47))

## [2.7.0](https://github.com/henn1001/QSDL/compare/v2.6.1...v2.7.0) (2022-05-28)


### Features

* **core:** add feature that allows to split domain model files ([77ee258](https://github.com/henn1001/QSDL/commit/77ee2588d3efbafe754080d51109b8f01aeb697f))
* **core:** introduce new generate directive to control the crud generation ([da16e35](https://github.com/henn1001/QSDL/commit/da16e357dc42c3ec2a9ce2d73040ed301a7c608e))
* **core:** introduce new pagination,produces and consumes directive ([c63a512](https://github.com/henn1001/QSDL/commit/c63a5125f35a4818dcd8d51af3d90e3ba07571c7))
* **spring:** add directive [@controller](https://gitlab.com/controller) to overwrite the name for controllers ([1f41e9a](https://github.com/henn1001/QSDL/commit/1f41e9a928754e7b6ccb11d8f3d7d5bfa5092f4e))
* **spring:** custom operations will no longer generate a DefaultService ([273a1ee](https://github.com/henn1001/QSDL/commit/273a1ee8db1b83ff72b3361dc1219128824e1084))
* **spring:** draft for customizable package structure ([9e41bcf](https://github.com/henn1001/QSDL/commit/9e41bcfde7776c2833d07c16269f96d52212f7aa))
* **spring:** introduce a controller interface to allow for more flexible implementation ([77fcaee](https://github.com/henn1001/QSDL/commit/77fcaeedb7b42c2d02eecb676c02da48baeecfe4))
* **spring:** only persist nested base types ([ef189ae](https://github.com/henn1001/QSDL/commit/ef189ae62255085eeb30bd5f8db3411502348540))
* **spring:** simplify service generation logic and improve parent queries for string identifier ([1dfb3ff](https://github.com/henn1001/QSDL/commit/1dfb3ffa6a166bb6c3a2ac53a4a12ce966ca9460))
* **spring:** support for uuid  identifiers by exposing uid as id ([a9ee2e7](https://github.com/henn1001/QSDL/commit/a9ee2e7f6dc2baa73a36e18e10b1d332a12c980c))
* **spring:** update spring-boot version and other various fixes ([e461ca3](https://github.com/henn1001/QSDL/commit/e461ca3fa3ba6b8b8b74bb49ca5f8fc52ac88f4a))


### Bug Fixes

* **core:** allow comments in enums ([ec9da3d](https://github.com/henn1001/QSDL/commit/ec9da3d32e45b08426862898fef79a274930d186))
* **openapi:** correct typo for ref pagination parameter ([1f04a98](https://github.com/henn1001/QSDL/commit/1f04a9878948196a57fe7db9bbb2efc60fe1f0a8))
* **spring:** re-enable nested bean validation because binder was in wrong config class ([dbf543b](https://github.com/henn1001/QSDL/commit/dbf543b3446a9255dd8b5e4fbe2dc439a7087906))
* **spring:** resolve issue in testcase for whenCountByXY_thenUseQuerie ([9893e7a](https://github.com/henn1001/QSDL/commit/9893e7a0c7aab4038ee30cc4f9bb4d11f49c190a))
* **spring:** resolve issue in testcase for whenRemoveXFromY_thenOk ([041ec44](https://github.com/henn1001/QSDL/commit/041ec44f493a5a927cea8f627524fba45ea5877d))
* **spring:** resolve issues with encapsulation flag generating erroneous code ([9d4f8e5](https://github.com/henn1001/QSDL/commit/9d4f8e50b07df02e861e74249f2ab99a5eaa465c))
* **spring:** resolve issues with missing objectnode import when using the controller directive ([3663f1c](https://github.com/henn1001/QSDL/commit/3663f1c9241d98b93ffafdc80aa820340dccb6f9))

### [2.6.1](https://github.com/henn1001/QSDL/compare/v2.6.0...v2.6.1) (2021-10-29)


### Bug Fixes

* **core:** resolve python 3.9 compatibility issue by moving to inquirer ([48e3165](https://github.com/henn1001/QSDL/commit/48e31659f1430547b6d0aed090a8df2b4060dcc4))
* **spring:** resolve issue missing error response for invalid aggregation requests ([783a700](https://github.com/henn1001/QSDL/commit/783a70095f601fa7933f6dee0430b7b6a055dd42))

## [2.6.0](https://github.com/henn1001/QSDL/compare/v2.5.0...v2.6.0) (2021-10-28)


### Features

* **spring:** add flyway for db migration and versioning ([d189ecc](https://github.com/henn1001/QSDL/commit/d189ecc53d228e506d5ce22b00cf705cdd335afb))
* **spring:** introduce profiles - switch from h2 to hsqldb - add postgresql support and docker-compose example ([1d57af3](https://github.com/henn1001/QSDL/commit/1d57af3c341e0841b2b9939baa10d3e42220b35d))
* **spring:** introduce querydsl - update and remove old logic and fix tests ([62a635b](https://github.com/henn1001/QSDL/commit/62a635b8163a6040f4c9ba30b666f0d858af5b94))
* **spring:** introduce querydsl for more typesafe querying ([c5cbea1](https://github.com/henn1001/QSDL/commit/c5cbea18f7e2f15f4e584c19396cb94237170d64))


### Bug Fixes

* **openapi:** add missing cursor parameters to types without query parameters and utilize a more generic query parameter with explode ([b2f8d07](https://github.com/henn1001/QSDL/commit/b2f8d07300e76c9d3a212db3e6b9520aec49e522))
* **openapi:** resolve issue with custom operations query parameters introduced in b2f8d073 ([387e7d5](https://github.com/henn1001/QSDL/commit/387e7d52f1f2de03f79b459de15e87aac395d182))
* **spring:** add datetimeformat information for querydsl and resolve clob compatibility with postgres ([bd005c7](https://github.com/henn1001/QSDL/commit/bd005c718cf33f304962eb920b7e06ba39988d9d))

## [2.5.0](https://github.com/henn1001/QSDL/compare/v2.4.0...v2.5.0) (2021-10-17)


### Features

* add global logger module ([b0d687e](https://github.com/henn1001/QSDL/commit/b0d687e43f87949780aa9178a61020ef007b99b7))
* **spring:** bump version for spring to 2.5.5 and java to 17 ([1eaa87f](https://github.com/henn1001/QSDL/commit/1eaa87fc0c70c4649206bf50f7af4d97470884b8))
* **spring:** prevent generation of unused entities ([38a9b97](https://github.com/henn1001/QSDL/commit/38a9b976c50ae9884810a50473d707dbc9c9051b))
* **spring:** repository tests now consider nested objects ([f4cb566](https://github.com/henn1001/QSDL/commit/f4cb56650e7294200992b5e513fff54b6df6eb1e))
* **spring:** rework and improve repository tests by changing the ownerside for aggregations ([2b7aa13](https://github.com/henn1001/QSDL/commit/2b7aa13b2914394136670b7a42f3c0355339ea91))


### Bug Fixes

* prevent non-array compositions ([6b0485c](https://github.com/henn1001/QSDL/commit/6b0485c87770bf711fae27957f3ae51bc1641184))
* **spring:** resolve issue with writing a "null" string into the database instead of null for objects ([746804d](https://github.com/henn1001/QSDL/commit/746804dbc0fba367187cf55fb046cb252e0d8c60))
* **spring:** resolve issues with nested base & objects by switching from elementcollection to OneToX ([2abd45a](https://github.com/henn1001/QSDL/commit/2abd45a6838f7de15f0124e3aefaadc67c23e4c3))

## [2.4.0](https://github.com/henn1001/QSDL/compare/v2.3.0...v2.4.0) (2021-09-23)


### Features

* add server path rules and a sane default value which connects to the spring generator ([6af2481](https://github.com/henn1001/QSDL/commit/6af2481d43d628ca431ef289033cdd0667d2f991))
* prevent argument name clashes for operations ([0c61d80](https://github.com/henn1001/QSDL/commit/0c61d802912d2a5443c2978089ecdcc8cc60f45e))
* **spring:** prepend an underscore to the internal uuid and version field for entities ([682db0f](https://github.com/henn1001/QSDL/commit/682db0fa6a6fc19ebc11656823bb9e36e90acb86))
* **spring:** use lombok for logging ([7c52ffb](https://github.com/henn1001/QSDL/commit/7c52ffb8376abb7a4188c18be65b7e6f3138b7b4))
* **spring:** utilize lombok for generating getter/setters and add a flag to config to enable this ([76be7df](https://github.com/henn1001/QSDL/commit/76be7dfe231f2b5152fae4b512225af58baba4a7))


### Bug Fixes

* **spring:** resolve issue with delete exceptions wrongly marked as entity not found ([273ba68](https://github.com/henn1001/QSDL/commit/273ba68e59271eaaeeeaf8524ec5d30b919141df))
* **spring:** resolve issue with failed payload test when object has no required fields ([a2f4a98](https://github.com/henn1001/QSDL/commit/a2f4a980ba5476ed502ce150078361fb95799c50))

## [2.3.0](https://github.com/henn1001/QSDL/compare/v2.2.0...v2.3.0) (2021-09-12)


### Features

* **grammar:** remove the nested directive to have a clear separation between relations and nested objects ([6a772e2](https://github.com/henn1001/QSDL/commit/6a772e202ed0e5a3b65984a29ecc021c912108f2))
* **spring:** added repository test generation ([cd31edb](https://github.com/henn1001/QSDL/commit/cd31edb44f97402116e1f35136aeb9a4326cdf47))
* **spring:** added test generation for controllers and services ([69913d1](https://github.com/henn1001/QSDL/commit/69913d123596db20046b9c4c3e64eeb442597ccf))
* **spring:** include relations in the encapsulation parameter ([72195f2](https://github.com/henn1001/QSDL/commit/72195f28de853e8126d5dce07be9cfacd0d4a76b))
* optimize count request for compositions and aggregations ([57aa44d](https://github.com/henn1001/QSDL/commit/57aa44d8b1f52a236e0a4cddf64f1d96cd312ac5))


### Bug Fixes

* **grammar:** allow use of hypens ([fa1eb11](https://github.com/henn1001/QSDL/commit/fa1eb11ab7d08a3b0152f5a48b6f5502bb64a9af))
* **spring:** resolve a relation parent finding issue ([22cca3b](https://github.com/henn1001/QSDL/commit/22cca3bf4eabfdc77cc635b028f85b78796098ef))
* **spring:** resolve issue regarding adding/removing aggregations with public fields ([8eb3fcd](https://github.com/henn1001/QSDL/commit/8eb3fcdc185f2225471053937a239b96bf6334c8))
* **spring:** resolve issues with nested bases and objects ([22109f4](https://github.com/henn1001/QSDL/commit/22109f4a0d1906adbb6aad743e86e9750fcadf2f))

## [2.2.0](https://github.com/henn1001/QSDL/compare/v2.1.0...v2.2.0) (2021-07-18)


### Features

* **core:** add various validation checks and rules to field directive usage ([37c3909](https://github.com/henn1001/QSDL/commit/37c390911cb0d9ebc089305f9157ad6804cf8d91))
* **spring:** add internal flag for public field access ([8ba74e0](https://github.com/henn1001/QSDL/commit/8ba74e0894f996acfe8da8a026a9b6aa248383c6))
* **spring:** added query parameter generation ([04fd528](https://github.com/henn1001/QSDL/commit/04fd5285acd7cce1ffbe611863a7d20905e18aab))
* **spring:** bump to java 16 and springboot 2.5.2 ([884ed11](https://github.com/henn1001/QSDL/commit/884ed11f6ed75e97e52b27eff5d17922bd69c6fe))
* **spring:** switch to ObjectNode for json objects ([cebe117](https://github.com/henn1001/QSDL/commit/cebe117f99c1efdf39d06a107d2b9a373600af14))
* **spring:** utilize text blocks for sql statements ([1a8c3fb](https://github.com/henn1001/QSDL/commit/1a8c3fb39936c84bc7dbb860147481e0931c04b7))
* removed the internal scalar ID in favor of assigning a id to all domain objects by default ([e04e89f](https://github.com/henn1001/QSDL/commit/e04e89fdee68b57cb52e0f57ef8d81a5c8ac4780))
* revert usage of object extensions "allof" for openapi ([fac7136](https://github.com/henn1001/QSDL/commit/fac713605dcc216f972df49f7b68d49dd8ff9547))


### Bug Fixes

* switch namespace of aggregation to parent ([5eebea1](https://github.com/henn1001/QSDL/commit/5eebea150cc9c6fe00e16de56b288a0bb7747429))
* **spring:** prevent unnecessary count queries on getall requests ([42a3d1b](https://github.com/henn1001/QSDL/commit/42a3d1b24056193bcf7d3aaa6c63629a7d9240ec))
* **spring:** resolve issue with nested base-types ([d020146](https://github.com/henn1001/QSDL/commit/d020146c5c5a71e4bfb22e14cf2f942471275f20))

## [2.1.0](https://github.com/henn1001/QSDL/compare/v2.0.0...v2.1.0) (2021-06-26)


### Features

* **spring:** final draft for database support - begin optimizing and testing ([713798e](https://github.com/henn1001/QSDL/commit/713798ea4486a3294043191a668b163c685483d0))
* **spring:** fourth draft for database support ([2ea9b14](https://github.com/henn1001/QSDL/commit/2ea9b142516952ea7d489d551cb756fa1b8bc9e5))
* **spring:** introduce abstract class with uuid and version to resolve object identification and introduce optimistic locking ([5fe757a](https://github.com/henn1001/QSDL/commit/5fe757acd436945fd2c510250ccf33d8d4dda157))
* **spring:** second draft for database support ([0a17abd](https://github.com/henn1001/QSDL/commit/0a17abd0e600e6f484bd245532f5e7e0e64f54b6))
* **spring:** third draft for database support ([051c736](https://github.com/henn1001/QSDL/commit/051c73611052ba208c080c1e5c8922a154a853f5))
* added a void generator that does nothing ([31e3775](https://github.com/henn1001/QSDL/commit/31e37750a73f96b29979602d279a96fe2f152aea))
* added minimal logging information ([02b072d](https://github.com/henn1001/QSDL/commit/02b072d0e76b80aa344e3dbddfc06441067482e7))

## [2.0.0](https://github.com/henn1001/QSDL/compare/v1.0.1...v2.0.0) (2021-06-20)


### ⚠ BREAKING CHANGES

* **grammar:** rename implements to extends as this is a more accurate description
* **grammar:** remove marker ( [value!] ) to indicate non-empty lists from language due to niche usage
* major refactoring and cleanup after recent changes for all generators
* switch default id_type to integer
* prepare for openapi 3.1 read/write only ref support
* introduce paging for list responses

### Features

* upgrade python package dependencies ([5992757](https://github.com/henn1001/QSDL/commit/59927572df83d658f6f26eb5ec087fa797c37379))
* **cli:** support for generator specific configuration list options ([ec5faab](https://github.com/henn1001/QSDL/commit/ec5faaba6361ec2f5d2922d8ed724832271569f3))
* **grammar:** remove marker ( [value!] ) to indicate non-empty lists from language due to niche usage ([0ffaf79](https://github.com/henn1001/QSDL/commit/0ffaf79fe9f3613e8a005fac198c7dfd65238e0b))
* **grammar:** rename implements to extends as this is a more accurate description ([b90c853](https://github.com/henn1001/QSDL/commit/b90c853c2520bc05f3fd399987c1b7ba06f8a329))
* **spring:** added beta version for a spring-boot generator ([b74d342](https://github.com/henn1001/QSDL/commit/b74d342ac266bf7d9089cbf58068ce73254f2e6d))
* **spring:** first draft for database support ([30fcdb6](https://github.com/henn1001/QSDL/commit/30fcdb611072f476559394b828a252c31c637976))
* add internal switch to change ID type for openAPI - mark ID attributes as such with custom attributes ([76e2593](https://github.com/henn1001/QSDL/commit/76e2593df93d6a36e2e4eca45039f25bb8dd9308))
* added modular generator logic and user prompt for the cli ([c3c2819](https://github.com/henn1001/QSDL/commit/c3c2819c65660f898078e21b447290caeb916612))
* added patch calls to modify any attributes  as opposed to put to replace a resource ([a0144ea](https://github.com/henn1001/QSDL/commit/a0144ea93f11201af0852fb14669144b6f27ed4f))
* commit srcgen for better change tracking ([c2cb208](https://github.com/henn1001/QSDL/commit/c2cb208b33fdfc491edfb7d08ee9af39d2ae9b92))
* introduce paging for list responses ([c1f0141](https://github.com/henn1001/QSDL/commit/c1f01412b4a4bc2e5de5c2ef6234f5a6df56459a))
* prepare for openapi 3.1 read/write only ref support ([a41bb3f](https://github.com/henn1001/QSDL/commit/a41bb3f862fdcb4546bb0b8d01762dfbb638c667))
* simplify error responses to default ([c4d7864](https://github.com/henn1001/QSDL/commit/c4d7864e6b4388059058859169ea27038e95a322))
* tag auto-generated crud operations ([2a2f49a](https://github.com/henn1001/QSDL/commit/2a2f49ae5aaf8f7c00965783c19b4a780534c10e))
* **OpenApi:** improve default error response ([3b3faf5](https://github.com/henn1001/QSDL/commit/3b3faf515a64630379561bc2924b0c7101c51528))


### Bug Fixes

* added missing usage of object dataclass ([c338962](https://github.com/henn1001/QSDL/commit/c338962960fd2756b05c11028ed45943c63ebf60))
* **OpenApi:** correctly use id_type for field values that are neither nested/aggregated/composed ([8dc04cf](https://github.com/henn1001/QSDL/commit/8dc04cf0dcee6380154cb2e39cce7e1feb9fab24))
* update and add dependencies for upcoming improvements ([acd806b](https://github.com/henn1001/QSDL/commit/acd806b71e588c39460e6a3c02d18b5d3a78b3a8))
* **grammar:** allow usage of numbers in enums ([8a3ff79](https://github.com/henn1001/QSDL/commit/8a3ff79b2426e37b0e06a842e45f30aadb1e9577))
* **OpenApi:** correct read/write-only for enums and added descriptions to parameters ([df16a3c](https://github.com/henn1001/QSDL/commit/df16a3c977b8b461dfc78b5202dbc862d369fb8e))


### Refactoring

* major refactoring and cleanup after recent changes for all generators ([e0cb400](https://github.com/henn1001/QSDL/commit/e0cb4004537ff6c62b67d117a732c3dbb27a1c72))
* switch default id_type to integer ([0a77eba](https://github.com/henn1001/QSDL/commit/0a77ebaf4270989d976357724636e7171cae5011))

## [1.0.1](https://github.com/henn1001/QSDL/compare/v1.0.0...v1.0.1) (2020-12-19)


### Features

* **OpenApi:** single arguments of scalar type "object" for custom operations omits the schema properties ([74a0757](https://github.com/henn1001/QSDL/commit/74a0757bc55c2884dd8bf85cd0270d173a6c9edf))
* add long and double scalar type ([d24ee30](https://github.com/henn1001/QSDL/commit/d24ee30a006284fbdbc1215593f1383168d3d73b))
* add operation sorting by order of input definition ([9614b0f](https://github.com/henn1001/QSDL/commit/9614b0f9c84669608190f99fcdb9055725b00d96))
* allow to enable/disable generators ([b47fc3a](https://github.com/henn1001/QSDL/commit/b47fc3acdf1dc0c0ded20952a40058f1388f18ba))
* convert inline enums into reusable enums ([43f41fe](https://github.com/henn1001/QSDL/commit/43f41fe837a373df218698125253bfafdb810c25))


### Bug Fixes

* **OpenApi:** required attribute in error schema referenced wrong value ([2cc42fb](https://github.com/henn1001/QSDL/commit/2cc42fb76b407416b727f403477ae58ab9e31e72))



## [1.0.0](https://github.com/henn1001/QSDL/compare/v0.1.0...v1.0.0) (2020-09-23)


### Features

* prevent usage of Void for Base and Object ([e605030](https://github.com/henn1001/QSDL/commit/e605030c129f7d480a851a15d77fcb4eaef46ce1))
* **cli:** add version option ([628d070](https://github.com/henn1001/QSDL/commit/628d070582bdf44abb928d706ad57083e54cb24e))
* added missing validators ([83960df](https://github.com/henn1001/QSDL/commit/83960df26b11026f81e55694dba453259127881a))
* implemented cli interface via click ([457b6dd](https://github.com/henn1001/QSDL/commit/457b6dd21e476bf9f7c90bcbdd8d7420d0972434))
* **grammar:** title, description, version and servers are now optional ([dce8043](https://github.com/henn1001/QSDL/commit/dce80430b94612280e7e669405937f66de878ed1))


### Bug Fixes

* **GraphQL:** nested inputs and custom queries and mutations ([f11311b](https://github.com/henn1001/QSDL/commit/f11311bd92d4576fefa6cb213f7d248d423f3156))
* **OpenAPI:** broken definition when no object type was specified ([25923a3](https://github.com/henn1001/QSDL/commit/25923a3252ce1e15de9a41f0e46a542f3666438c))
* fixed bug with custom operation payload parameter types ([452dead](https://github.com/henn1001/QSDL/commit/452dead0a3f3e52bf45b24f4813baaf4721a21b0))
* **OpenAPI:** fixed regression with base type generation ([e82fe8b](https://github.com/henn1001/QSDL/commit/e82fe8b12c9b83cba4e053a0b81d2c3fa122e99c))
* **OpenAPI:** generate base types regardless of usage ([3114280](https://github.com/henn1001/QSDL/commit/3114280126bf5ee307ec0aa67b610ef4f2cb2604))



## [0.1.0](https://github.com/henn1001/QSDL/compare/7e1100ab6b8fe41fdf073b193fca501f635bb666...v0.1.0) (2020-08-07)


### Features

* hello world from QSDL ([7e1100a](https://github.com/henn1001/QSDL/commit/7e1100ab6b8fe41fdf073b193fca501f635bb666))
