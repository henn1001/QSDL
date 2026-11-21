package app.api.order.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import app.TestUtils;
import app.api.order.OrderPlacementService;
import app.api.order.contract.Order;
import app.api.order.contract.OrderRequest;
import app.api.order.contract.UpdateOrderStatusRequest;
import app.shared.constants.OrderStatus;
import app.shared.util.JsonUtil;
import org.json.JSONObject;
import org.junit.jupiter.api.Test;
import org.skyscreamer.jsonassert.JSONAssert;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(OrderPlacementController.class)
class OrderPlacementControllerTest {

    @MockitoBean
    OrderPlacementService orderPlacementService;

    @Autowired
    MockMvc mockMvc;

    @Test
    void whenPlaceOrder_thenOk() throws Exception {
        OrderRequest request = TestUtils.getRandom(OrderRequest.class);
        Order responseDto = TestUtils.getRandom(Order.class);
        when(orderPlacementService.placeOrder(any())).thenReturn(responseDto);

        String response = mockMvc.perform(post("/api/v1/orders/place")
                        .content(JsonUtil.toString(request))
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        JSONAssert.assertEquals(JsonUtil.toString(responseDto), new JSONObject(response), false);
    }

    @Test
    void whenUpdateOrderStatus_thenOk() throws Exception {
        UpdateOrderStatusRequest request = new UpdateOrderStatusRequest(OrderStatus.APPROVED);
        Order responseDto = TestUtils.getRandom(Order.class);
        when(orderPlacementService.updateStatus(eq(1L), any())).thenReturn(responseDto);

        String response = mockMvc.perform(patch("/api/v1/orders/1/status")
                        .content(JsonUtil.toString(request))
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        JSONAssert.assertEquals(JsonUtil.toString(responseDto), new JSONObject(response), false);
    }
}
