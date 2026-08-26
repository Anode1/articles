package demo;

import java.util.List;
import org.springframework.data.repository.Repository;

public interface ItemRepository extends Repository<Item, Long> {
    List<Item> findAllByOrderById();
    List<Item> findByAuthorOrderById(String author);
    Item save(Item item);
}
