#!/usr/bin/python3
"""
Entry point to my application
"""

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import List


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_prime(n: int) -> bool:
    """
    Determines if a number is a prime number.

    A prime number is a natural number greater than 1 that is not a product
    of two smaller natural numbers. This function checks if the given integer
    n is a prime number.

    Args:
        n (int): The number to check for primality.

    Returns:
        bool: True if n is a prime number, False otherwise.
    """

    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    j = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += j
        j = 6 - j
    return True


def is_perfect(n: int) -> bool:
    """
    Returns true if n is a perfect number, false otherwise.

    A perfect number is a positive integer that is equal to the sum of its
    proper divisors, excluding the number itself.
    """

    if n <= 1:
        return False
    sum_divisors = 1
    sqrt_n = int(n**0.5)
    for i in range(2, sqrt_n + 1):
        if n % i == 0:
            sum_divisors += i
            if i != n // i:
                sum_divisors += n // i
    return sum_divisors == n


def is_armstrong(n: int) -> bool:
    """Returns true if n is an armstrong number, false otherwise.

    An armstrong number is a number that is equal to the sum of its own
    digits each raised to the power of the number of digits.
    """

    num_str = str(abs(n))
    length = len(num_str)
    return sum(int(digit) ** length for digit in num_str) == abs(n)


async def get_fun_fact(n: int) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://numbersapi.com/{n}/math", timeout=3.0)
            if response.status_code == 200:
                return response.text
            return "No fun fact available"
    except (httpx.RequestError, httpx.TimeoutException):
        return "No fun fact available"


def validate_number(number: str) -> int:
    """Validate and convert number string to integer"""
    try:
        return int(number)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"number": number, "error": True},
        )


@app.get("/api/classify-number", response_model=dict)
async def classify_number(number: str = Query(..., description="Number to classify")):
    try:
        num = validate_number(number)
    except HTTPException as e:
        return JSONResponse(content=e.detail, status_code=e.status_code)

    properties = []

    parity = "even" if num % 2 == 0 else "odd"

    armstrong = is_armstrong(num)
    if armstrong:
        properties.append("armstrong")

    properties.append(parity)

    fun_fact = await get_fun_fact(num)

    return {
        "number": num,
        "is_prime": is_prime(num),
        "is_perfect": is_perfect(num),
        "properties": properties,
        "digit_sum": sum(int(d) for d in str(abs(num))),
        "fun_fact": fun_fact,
    }
