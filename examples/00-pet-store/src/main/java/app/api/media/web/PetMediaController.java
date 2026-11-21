/**
 * NOTE: Hand-maintained overlay implementing PetMedia file storage endpoints.
 */
package app.api.media.web;

import app.api.media.PetMediaService;
import app.api.media.contract.DownloadPetMediaFilter;
import app.api.media.contract.ListPetMediaFilter;
import app.api.media.contract.PetMedia;
import app.api.media.contract.UploadPetMediaRequest;
import app.shared.web.BaseController;
import java.util.List;
import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;

@Controller
@AllArgsConstructor
public class PetMediaController extends BaseController implements PetMediaApi {

    final PetMediaService petmediaService;

    @Override
    public ResponseEntity<PetMedia> uploadPetMedia(UploadPetMediaRequest request) {
        return new ResponseEntity<>(petmediaService.upload(request), HttpStatus.CREATED);
    }

    @Override
    public ResponseEntity<List<PetMedia>> listPetMedia(ListPetMediaFilter filter) {
        return new ResponseEntity<>(petmediaService.listForPet(filter.petId()), HttpStatus.OK);
    }

    @Override
    public ResponseEntity<byte[]> downloadPetMedia(DownloadPetMediaFilter filter) {
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(petmediaService.download(filter.petId(), filter.mediaId()));
    }
}
