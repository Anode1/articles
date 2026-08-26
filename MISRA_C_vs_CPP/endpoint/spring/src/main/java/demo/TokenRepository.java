package demo;

import org.springframework.data.repository.Repository;

public interface TokenRepository extends Repository<Token, String> {
    boolean existsByToken(String token);
}
