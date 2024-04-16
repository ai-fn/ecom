package auth

import (
	"fmt"
	"net/http"

	"github.com/dgrijalva/jwt-go"
	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		var scKey string = "django-insecure-dqm6w2nl1q2i!%t%+z1*r)!-%8lg9@fm81k&ms$2z2pnej3%xt"

		tokenStr := c.Request.Header.Get("Authorization")[7:]
		token, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(scKey), nil
		})

		if err != nil || !token.Valid {
			fmt.Println(err.Error(), token.Valid)
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid or expired token"})
			c.Abort()
			return
		}

		c.Next()
	}
}
