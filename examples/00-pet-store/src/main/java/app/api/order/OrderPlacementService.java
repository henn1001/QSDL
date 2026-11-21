package app.api.order;

import app.api.order.contract.Order;
import app.api.order.contract.OrderRequest;
import app.api.order.contract.UpdateOrderStatusRequest;
import app.api.order.mapping.OrderMapper;
import app.api.order.persistence.OrderEntity;
import app.api.order.persistence.OrderRepository;
import app.shared.constants.OrderStatus;
import app.shared.exception.AppException;
import app.shared.exception.AppExceptionUtil;
import app.shared.util.TimeUtil;
import java.time.OffsetDateTime;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Hand-maintained application service for order placement and status transitions. */
@Service
@RequiredArgsConstructor
public class OrderPlacementService {

    final OrderRepository orderRepository;
    final OrderMapper orderMapper;

    @Transactional
    public Order placeOrder(OrderRequest request) throws AppException {
        OrderEntity entity = orderMapper.toEntity(request);
        OffsetDateTime now = TimeUtil.now();
        entity.setStatus(request.status() != null ? request.status() : OrderStatus.PLACED);
        entity.setCreatedAt(now);
        entity.setUpdatedAt(now);
        return orderMapper.toResponse(orderRepository.save(entity));
    }

    @Transactional
    public Order updateStatus(Long id, UpdateOrderStatusRequest request) throws AppException {
        OrderEntity entity = orderRepository.findById(id)
                .orElseThrow(() -> AppExceptionUtil.entityNotFound(Order.class, id));
        entity.setStatus(request.status());
        entity.setUpdatedAt(TimeUtil.now());
        return orderMapper.toResponse(orderRepository.save(entity));
    }
}
