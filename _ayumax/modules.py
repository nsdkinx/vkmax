async def token_write(token: str):
    print(token)
    token_file = open("token.txt", "w+")
    token_file.write(token)

async def token_read():
    with open("token.txt", "r") as file:
        content = file.read()
        file.close()
    return content