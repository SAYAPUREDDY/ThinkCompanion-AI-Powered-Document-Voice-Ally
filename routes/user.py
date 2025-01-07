from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database.users import User_database
from models.users import user_signup,user_login,TokenModel
from functions.user import user_functions
from fastapi.encoders import jsonable_encoder


router = APIRouter()

user_database = User_database()

@router.post("/sign_up")
async def sign_up(user:user_signup):
    user=jsonable_encoder(user)
    user["password"] = await user_functions.get_password_hash(user["password"])
    try:
        new_user = await user_database.add_user(user)
        # print(status)
        # if status == 1:
            # return JSONResponse({"message": "User added successfully"}, status_code=201)
        # else:
            # return JSONResponse({"message": "User already exists"}, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    token=  await user_functions.create_access_token({"user": new_user}) 
    return {"message": "User added successfully","access_token":token, "type": "bearer"}
    

@router.post("/login")
async def login(user:user_login):
    try:
        user = await user_functions.authenticate_user(user.email, user.password)
        if user:
            token =  await user_functions.create_access_token({"user": user})
            return JSONResponse({"message": "Login successful","access_token": token, "type": "bearer","User_ID":user["id"]  })
        else:
            return JSONResponse({"message": "Invalid credentials"}, status_code=401)
        #     if user:
    #         return JSONResponse({"message": "Login successful"}, status_code=200)
    #     else:
    #         return JSONResponse({"message": "Invalid credentials"}, status_code=401)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/send_verification_mail")
async def send_verification_mail(email:str):
    verification_token = await user_functions.generate_verification_token()
    user = await User_database.get_user_from_email(email)
    user["verification_code"]=verification_token
    count = await User_database.update_user(user["id"],user)
    # Send the verification email
    mail = await user_functions.send_email(email,verification_token)
    if mail=="sent":   
        return {"message":"Verification mail sent"}
    else:
        raise HTTPException(status_code=403, detail="Failed to send mail")

@router.post("/verify_email")
async def verify_email(email:str,verification_code:str):
    user = await User_database.get_user_from_email(email)
    if user["verification_code"]== verification_code:
        user["verified"]=1
        count = await User_database.update_user(user["id"],user)
        if  count==1:
            return {"message":"Verified Succesfully"}
        else:
            return {"message":"Incorrect Verification code"}
    else:
        return {"message":"Incorrect Verification code"}

