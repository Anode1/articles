package demo;

import java.util.List;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
public class ItemController {
    private final ItemRepository items;

    public ItemController(ItemRepository items) { this.items = items; }

    @GetMapping("/items")
    public List<Item> list(@RequestParam(required = false) String author) {
        return author == null ? items.findAllByOrderById()
                              : items.findByAuthorOrderById(author);
    }

    @PostMapping("/items")
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Long> add(@RequestBody Item item) {
        return Map.of("id", items.save(item).getId());
    }
}
