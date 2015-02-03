package main

import (
	"fmt"
	"math"
)

// Horner's Method to hash string of length L (O(L))
func hashCodeString(s string) int {
	hash := int32(0)
	for i := 0; i < len(s); i++ {
		hash = int32(hash<<5-hash) + int32(s[i])
		hash &= hash
	}
	return int(math.Abs(float64(hash)))
}

func hashCodeRunes(r []rune) int {
	hash := int32(0)
	for i := 0; i < len(r); i++ {
		hash = int32(hash<<5-hash) + int32(r[i])
		hash &= hash
	}
	return int(math.Abs(float64(hash)))
}


func main() {
	s := "Hello, playground. 日本語!"
	fmt.Println(s)
	fmt.Println(hashCodeString(s))
	fmt.Println(hashCodeRunes([]rune(s)))
}


// Hello, playground. 日本語!
// 962985018
// 799803075
