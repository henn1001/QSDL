/**
 * NOTE: Hand-maintained overlay implementing order placement and status transitions.
 */
package app.api.order.web;

import app.api.order.OrderPlacementService;
import app.api.order.contract.Order;
import app.api.order.contract.OrderRequest;
import app.api.order.contract.UpdateOrderStatusRequest;
import app.shared.web.BaseController;
import lombok.AllArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;

@Controller
@AllArgsConstructor
public class OrderPlacementController extends BaseController implements OrderPlacementApi {

    final OrderPlacementService orderPlacementService;

    @Override
    public ResponseEntity<Order> placeOrder(OrderRequest order) {
        return new ResponseEntity<>(orderPlacementService.placeOrder(order), HttpStatus.OK);
    }

    @Override
    public ResponseEntity<Order> updateOrderStatus(Long orderId, UpdateOrderStatusRequest request) {
        return new ResponseEntity<>(orderPlacementService.updateStatus(orderId, request), HttpStatus.OK);
    }
}
