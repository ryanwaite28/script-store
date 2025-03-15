package com.modernapps.maverick.gateway_api.config;

import io.jsonwebtoken.*;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

@Component
public class JwtUtilsConfig {

    // Secret key for signing the JWT
    private final String SECRET_KEY;  // Keep this safe!

    // Expiration time in milliseconds (e.g., 1 hour)
    private final long EXPIRATION_TIME = (1000 * 60 * 60 * 24 * 7);  // 1 week

    public JwtUtilsConfig(@Value("${auth.jwt.secret}") String authJwtSecret) {
        this.SECRET_KEY = authJwtSecret;
    }

    // Create a JWT token
    public String createToken(String userId) {
        return Jwts.builder()
            .claims(Map.ofEntries(
                Map.entry("userId", userId)
            ))
            .subject(userId)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + this.EXPIRATION_TIME))
            .signWith(createSigningKey())
            .compact();  // Return the JWT string
    }

    public String verifyToken(String token) {
        try {
            Jws<Claims> claimsJws = Jwts.parser()
                .verifyWith(this.createSigningKey())
                .build()
                .parseSignedClaims(token);

            return claimsJws.getPayload().getSubject();
        } catch (JwtException | IllegalArgumentException e) {
            // Handle token errors (expired, invalid, etc.)
            System.out.println("Token verification failed: " + e.getMessage());
            throw e;
        }
    }

    // Check if a token is expired
    public boolean isTokenExpired(String token) {
        try {
            Jws<Claims> claimsJws = Jwts.parser()
                .verifyWith(this.createSigningKey())
                .build()
                .parseSignedClaims(token);

            Date expirationDate = claimsJws.getPayload().getExpiration();
            return expirationDate.before(new Date());
        } catch (JwtException | IllegalArgumentException e) {
            return true;  // If token is invalid or expired
        }
    }

    // Helper method to create the signing key
    private SecretKey createSigningKey() {
        SecretKey key = Keys.hmacShaKeyFor(this.SECRET_KEY.getBytes(StandardCharsets.UTF_8));
        return key;
    }
}