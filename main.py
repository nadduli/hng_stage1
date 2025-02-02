#!/usr/bin/python3
"""
Entry point to my application
"""

from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_prime(n: int) -> bool:
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
    """Check if a number is an Armstrong number (narcissistic number)"""
    if n < 0:
        return False
    num_str = str(n)
    length = len(num_str)
    # Explicitly handle single-digit numbers and zero
    if length == 1:
        return n == 0  # Only 0 is considered Armstrong in single-digit
    return sum(int(digit)**length for digit in num_str) == n

async def get_fun_fact(n: int) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://numbersapi.com/{n}/math",
                timeout=3.0
            )
            return response.text if response.status_code == 200 else "No fun fact available"
    except (httpx.RequestError, httpx.TimeoutException):
        return "No fun fact available"

@app.get("/api/classify-number", response_model=dict)
async def classify_number(number: str = Query(..., description="Number to classify")):
    try:
        num = int(number)
    except ValueError:
        return JSONResponse(
            content={"number": number, "error": True},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    armstrong = is_armstrong(num)
    parity = "even" if num % 2 == 0 else "odd"
    
    properties = []
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
        "fun_fact": fun_fact
    }