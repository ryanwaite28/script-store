package com.modernapps.maverick.gateway_api.config;

import com.modernapps.maverick.gateway_api.annotations.JwtAuthorized;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;

@Aspect
@Component
public class JwtAuthenticationAspect {

    // Intercept methods annotated with @JwtAuthorized
    @Before("@annotation(com.modernapps.maverick.gateway_api.annotations.JwtAuthorized)")
    public void extractAuthenticationToken(JoinPoint joinPoint) {
        // Retrieve the authentication token from the SecurityContextHolder
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        boolean isAuthorized = authentication != null && authentication.isAuthenticated();

        // Get the method being called
        Method method = ((MethodSignature) joinPoint.getSignature()).getMethod();
        // Check if the method has the CustomAuth annotation
        JwtAuthorized jwtAuthorized = method.getAnnotation(JwtAuthorized.class);

        boolean shouldThrowError = jwtAuthorized != null && (!isAuthorized && !jwtAuthorized.suppressError());
        if (shouldThrowError) {
            throw new RuntimeException("Not JWT Authorized");
        }
    }

}
