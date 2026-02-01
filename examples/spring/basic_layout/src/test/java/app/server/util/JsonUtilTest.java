package app.server.util;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.lang.reflect.Field;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import tools.jackson.databind.JacksonModule;
import tools.jackson.databind.cfg.MapperBuilder;
import tools.jackson.databind.json.JsonMapper;

@SpringBootTest
class JsonUtilTest {

    @Autowired
    private JsonMapper springManagedMapper;

    private JsonMapper customConfiguredMapper;

    @BeforeEach
    void setup() {
        customConfiguredMapper = JsonUtil.mapper();
    }

    @Test
    void shouldHaveSameRegisteredModulesAsSpringMapper() {
        var spring = springManagedMapper.rebuild();
        var custom = customConfiguredMapper.rebuild();

        @SuppressWarnings("unchecked")
        var springModules = (Map<Object, JacksonModule>) getBuilderField(spring, "_modules");
        @SuppressWarnings("unchecked")
        var customModules = (Map<Object, JacksonModule>) getBuilderField(custom, "_modules");

        assertEquals(springModules.size(), customModules.size(), "Module count should match");
        assertEquals(springModules.keySet(), customModules.keySet(), "Module registration IDs should match");

        for (Object registrationId : springModules.keySet()) {
            JacksonModule springModule = springModules.get(registrationId);
            JacksonModule customModule = customModules.get(registrationId);

            assertEquals(
                    springModule.getRegistrationId(),
                    customModule.getRegistrationId(),
                    "Module registration ID should match");
            assertEquals(
                    springModule.getModuleName(),
                    customModule.getModuleName(),
                    "Module name should match for registration ID: " + registrationId);
        }
    }

    @Test
    void shouldHaveSameFeatureConfigurationAsSpringMapper() {
        var spring = springManagedMapper.rebuild();
        var custom = customConfiguredMapper.rebuild();

        assertEquals(getBuilderField(spring, "_deserFeatures"), getBuilderField(custom, "_deserFeatures"));
        assertEquals(getBuilderField(spring, "_serFeatures"), getBuilderField(custom, "_serFeatures"));
        assertEquals(getBuilderField(spring, "_mapperFeatures"), getBuilderField(custom, "_mapperFeatures"));
        assertEquals(getBuilderField(spring, "_streamReadFeatures"), getBuilderField(custom, "_streamReadFeatures"));
        assertEquals(getBuilderField(spring, "_streamWriteFeatures"), getBuilderField(custom, "_streamWriteFeatures"));
        assertEquals(getBuilderField(spring, "_formatReadFeatures"), getBuilderField(custom, "_formatReadFeatures"));
        assertEquals(getBuilderField(spring, "_formatWriteFeatures"), getBuilderField(custom, "_formatWriteFeatures"));
    }

    private static Object getBuilderField(Object target, String fieldName) {
        try {
            Field field = MapperBuilder.class.getDeclaredField(fieldName);
            field.setAccessible(true);
            return field.get(target);
        } catch (ReflectiveOperationException e) {
            throw new RuntimeException("Failed to access field: " + fieldName, e);
        }
    }
}
