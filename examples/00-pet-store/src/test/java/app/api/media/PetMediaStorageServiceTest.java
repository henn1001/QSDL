package app.api.media;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class PetMediaStorageServiceTest {
    @TempDir Path tempDir;
    private PetMediaStorageService storage;

    @BeforeEach
    void setUp() throws IOException {
        storage = new PetMediaStorageService(tempDir.toString());
    }

    @AfterEach
    void cleanUp() throws IOException {
        // TempDir owns cleanup; this keeps the test explicit about no runtime storage is retained.
        Files.walk(tempDir).sorted(Comparator.reverseOrder()).filter(path -> !path.equals(tempDir))
                .forEach(path -> path.toFile().delete());
    }

    @Test
    void storesAndResolvesMediaByOpaqueKey() throws Exception {
        String key = storage.store("42", "photo.jpg", new ByteArrayInputStream(new byte[] {1, 2, 3}));
        assertThat(key).startsWith("42/");
        assertThat(Files.readAllBytes(storage.resolve(key))).containsExactly(1, 2, 3);
    }

    @Test
    void rejectsTraversalAndUnsafeFilenames() {
        assertThatThrownBy(() -> storage.store("../42", "photo.jpg", new ByteArrayInputStream(new byte[0])))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> storage.store("42", "../photo.jpg", new ByteArrayInputStream(new byte[0])))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> storage.resolve("42/../../secret"))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> storage.resolve("../42/file"))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void rejectsMissingAndSymlinkedFiles() throws Exception {
        assertThatThrownBy(() -> storage.resolve("42/missing.jpg")).isInstanceOf(IOException.class);
        Path directory = tempDir.resolve("42");
        Files.createDirectories(directory);
        Path outside = tempDir.resolve("outside.txt");
        Files.writeString(outside, "secret");
        try {
            Files.createSymbolicLink(directory.resolve("link.txt"), outside);
        } catch (UnsupportedOperationException | IOException exception) {
            return; // Symlinks are unavailable on some Windows CI configurations.
        }
        assertThatThrownBy(() -> storage.resolve("42/link.txt")).isInstanceOf(IOException.class);
    }

    @Test
    void rejectsOversizedUploadsAndRemovesPartialFile() {
        byte[] content = new byte[(int) PetMediaStorageService.MAX_UPLOAD_BYTES + 1];
        assertThatThrownBy(() -> storage.store("42", "large.bin", new ByteArrayInputStream(content)))
                .isInstanceOf(IOException.class);
        assertThat(Files.exists(tempDir.resolve("42"))).isFalse();
    }
}
