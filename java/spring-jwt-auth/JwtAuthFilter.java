package com.modernapps.maverick.gateway_api.config.requestfilters;

import com.modernapps.maverick.gateway_api.config.JwtUtilsConfig;
import com.modernapps.maverick.gateway_api.constants.AuthorityNames;
import com.modernapps.maverick.gateway_api.constants.RequestAttributeNames;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import java.io.IOException;
import java.util.List;
import java.util.UUID;


public class JwtAuthFilter extends OncePerRequestFilter {

    private JwtUtilsConfig jwtUtilsConfig;

    public JwtAuthFilter(JwtUtilsConfig jwtUtilsConfig) {
        this.jwtUtilsConfig = jwtUtilsConfig;
    }

    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain filterChain
    ) throws ServletException, IOException {
        // Get JWT token from the request header
        String token = request.getHeader("Authorization");

        // Check if token is valid
        boolean isBearerToken = token != null && token.startsWith("Bearer ");
        if (isBearerToken) {
            token = token.substring(7); // Remove "Bearer " prefix
            try {
                String userId = this.jwtUtilsConfig.verifyToken(token);
                SimpleGrantedAuthority authority = new SimpleGrantedAuthority(AuthorityNames.JWT_AUTHORITY);
                UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(userId, null, List.of(authority)); // You could add authorities here
                SecurityContextHolder.getContext().setAuthentication(authenticationToken);

                request.setAttribute(RequestAttributeNames.JWT_AUTH_TOKEN, token);
                request.setAttribute(RequestAttributeNames.JWT_AUTH_USERID, UUID.fromString(userId));

                System.out.println("[JwtAuthFilter] request jwt authorized");
            }
            catch (Exception ex) {
                // not jwt authorized
                System.out.println("[JwtAuthFilter] request jwt authorization failed");
                System.out.println(ex.getMessage());
                ex.printStackTrace();
            }
        }

        filterChain.doFilter(request, response);
    }
}