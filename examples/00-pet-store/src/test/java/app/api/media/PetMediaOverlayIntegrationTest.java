package app.api.media;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import app.api.catalog.PetService;
import app.api.catalog.contract.Pet;
import app.api.catalog.contract.PetRequest;
import app.api.general.contract.Address;
import app.api.media.contract.PetMedia;
import app.api.media.persistence.PetMediaRepository;
import app.api.order.contract.Order;
import app.api.order.contract.OrderRequest;
import app.api.order.contract.UpdateOrderStatusRequest;
import app.shared.constants.OrderStatus;
import app.shared.constants.PetStatus;
import app.shared.util.JsonUtil;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.jdbc.Sql;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("h2")
@Transactional
class PetMediaOverlayIntegrationTest {

    @TempDir
    static Path storageDir;

    @DynamicPropertySource
    static void configureStorage(DynamicPropertyRegistry registry) {
        registry.add("pet-media.storage-directory", () -> storageDir.toString());
        registry.add("spring.datasource.url", () -> "jdbc:h2:mem:overlaytestdb;MODE=PostgreSQL");
    }

    @Autowired
    MockMvc mockMvc;

    @Autowired
    PetService petService;

    @Autowired
    PetMediaRepository petMediaRepository;

    @Test
    @Sql("/db/migration/V1_0_1__pet_media_pet_reference.sql")
    @Sql(statements = "ALTER TABLE t_pet_media DROP CONSTRAINT fk_t_pet_media_pet",
            executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
    void uploadListAndDownloadPetMedia() throws Exception {
        Pet pet = petService.createPet(new PetRequest("Buddy", PetStatus.AVAILABLE, null, null, null));
        byte[] payload = "pet-photo-bytes".getBytes(StandardCharsets.UTF_8);
        PetMedia uploaded = upload(pet.id(), "photo.jpg", payload);
        PetMedia other = upload(pet.id(), "other.jpg", payload);
        assertThat(uploaded.id()).isNotNull().isNotEqualTo(other.id());
        assertThat(uploaded.pet().id()).isEqualTo(pet.id());
        assertThat(other.pet().id()).isEqualTo(pet.id());

        String listJson = mockMvc.perform(get("/api/v1/pets/media")
                        .param("pet_id", String.valueOf(pet.id())))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
        assertThat(listJson).contains("photo.jpg", "other.jpg");
        assertThat(JsonUtil.fromJson(listJson, PetMedia[].class))
                .extracting(media -> media.pet().id())
                .containsExactly(pet.id(), pet.id());

        mockMvc.perform(get("/api/v1/pets/media/download")
                        .param("pet_id", String.valueOf(pet.id()))
                        .param("media_id", String.valueOf(uploaded.id())))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_OCTET_STREAM))
                .andExpect(content().bytes(payload));

        petMediaRepository.deleteById(uploaded.id());
        petMediaRepository.flush();
        assertThat(petMediaRepository.existsById(uploaded.id())).isFalse();
        assertThat(petMediaRepository.existsById(other.id())).isTrue();
        assertThat(petService.getPet(pet.id()).id()).isEqualTo(pet.id());
    }

    @Test
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    void deletingPetMakesExistingMediaUndownloadable() throws Exception {
        Pet pet = petService.createPet(new PetRequest("Buddy", PetStatus.AVAILABLE, null, null, null));
        byte[] payload = "pet-photo-bytes".getBytes(StandardCharsets.UTF_8);
        PetMedia media = upload(pet.id(), "photo.jpg", payload);
        Path file = storageDir.resolve(media.storageKey());
        assertThat(file).exists();
        var download = get("/api/v1/pets/media/download")
                .param("pet_id", String.valueOf(pet.id()))
                .param("media_id", String.valueOf(media.id()));
        mockMvc.perform(download).andExpect(status().isOk()).andExpect(content().bytes(payload));

        mockMvc.perform(delete("/api/v1/pets/{id}", pet.id())).andExpect(status().isOk());

        mockMvc.perform(download).andExpect(status().isNotFound());
        assertThat(petMediaRepository.existsById(media.id())).isTrue();
        assertThat(file).exists();
        petMediaRepository.deleteById(media.id());
    }

    private PetMedia upload(Long petId, String filename, byte[] payload) throws Exception {
        MockMultipartFile file = new MockMultipartFile("file", filename, "image/jpeg", payload);
        String uploadJson = mockMvc.perform(multipart("/api/v1/pets/media/upload")
                        .file(file)
                        .param("pet_id", String.valueOf(petId))
                        .param("media_type", "image/jpeg")
                        .param("filename", filename))
                .andExpect(status().isCreated())
                .andReturn()
                .getResponse()
                .getContentAsString();
        return JsonUtil.fromJson(uploadJson, PetMedia.class);
    }

    @Test
    void placeOrderAndUpdateOrderStatus() throws Exception {
        OrderRequest placeRequest = new OrderRequest(null, new Address("Main St 1", "Berlin", "10115"));

        String placedJson = mockMvc.perform(post("/api/v1/orders/place")
                        .content(JsonUtil.toString(placeRequest))
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        Order placed = JsonUtil.fromJson(placedJson, Order.class);
        assertThat(placed.id()).isNotNull();
        assertThat(placed.status()).isEqualTo(OrderStatus.PLACED);
        assertThat(placed.createdAt()).isNotNull();

        String updatedJson = mockMvc.perform(patch("/api/v1/orders/" + placed.id() + "/status")
                        .content(JsonUtil.toString(new UpdateOrderStatusRequest(OrderStatus.DELIVERED)))
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        Order updated = JsonUtil.fromJson(updatedJson, Order.class);
        assertThat(updated.status()).isEqualTo(OrderStatus.DELIVERED);
    }
}
