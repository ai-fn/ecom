package auth

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"log"
	"models"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"golang.org/x/crypto/pbkdf2"
)

func AuthMiddleware(db *gorm.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the username and password from the request headers
		var login models.Login
		if err := c.BindJSON(&login); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
			return
		}

		// Access the username, password, and other fields from loginData
		username := login.Username
		password := login.Password

		fmt.Println(username, password)

		usrnm, err := authenticate(db, username, password)
		if err != nil {
			// If credentials are incorrect or not provided, return 401 Unauthorized
			c.JSON(http.StatusUnauthorized, gin.H{"error": err.Error()})
			return
		}

		fmt.Printf("User %s send request", usrnm)

		// Call the next handler in the chain
		c.Next()
	}
}

// Authenticate user credentials using Gorm
func authenticate(db *gorm.DB, username, password string) (string, error) {
	var user models.CustomUser
	if db == nil {
		fmt.Print("Error")
		return "", fmt.Errorf("error")
	}

	if err := db.Where("username = ?", username).First(&user).Error; err != nil {
		if gorm.IsRecordNotFoundError(err) {
			return "", fmt.Errorf("invalid username or password")
		}
		log.Fatal(err.Error())
		return "", err
	}

	// Compare the provided password with the hashed password from the database
	if DjangoPasswordIsValid(password, user.Password) {
		return username, nil
	}
	return "", fmt.Errorf("invalid credentials")
}

func DjangoPasswordIsValid(password, hashedPassword string) bool {
	// Split the Django password hash into its components
	parts := strings.Split(hashedPassword, "$")
	if len(parts) != 4 {
		return false // Invalid password hash format
	}

	iterCount, _ := strconv.Atoi(parts[1])
	salt := parts[2]
	hash := parts[3]

	// Derive key from provided password and salt using PBKDF2
	derivedKey := pbkdf2.Key([]byte(password), []byte(salt), iterCount, 32, sha256.New)

	// Encode the derived key as base64
	encodedKey := base64.StdEncoding.EncodeToString(derivedKey)

	// Compare the derived key with the stored hash
	return subtle.ConstantTimeCompare([]byte(encodedKey), []byte(hash)) == 1
}
