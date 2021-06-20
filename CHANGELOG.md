# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

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
