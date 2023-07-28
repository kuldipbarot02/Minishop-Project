from django.shortcuts import render,redirect
from . models import User,Product,Wishlist,Cart
from django.conf import settings
from django.core.mail import send_mail
import random
import requests

import stripe
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'

# Create your views here.
def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)


def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method=="POST":
         try:
            User.objects.get(email=request.POST['email'])
            msg="Email allredy Regiesterd"
            return render (request,'signup.html',{'msg':msg})
         except:
             if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    usertype=request.POST['usertype'],
                )
                msg="User Sign Up Successfully"
                return render(request,'signup.html',{'msg':msg})
             else:
                msg="Password & Confirom Does Not Matched"
                return render(request,'signup.html',{'msg':msg})

    else:
        return render (request,'signup.html')

def login(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                request.session['email']=user.email
                request.session['fname']=user.fname
                if user.usertype=="buyer":
                    wishlist=Wishlist.objects.filter(user=user)
                    request.session['wishlist_count']=len(wishlist)
                    carts=Cart.objects.filter(user=user,payment_status=False)
                    request.session['cart_count']=len(carts)  
                    return render(request,'index.html')
                else:
                    return render(request,'seller-index.html')
            else:
                msg="Incorrect Password"
                return render(request,'login.html',{'msg':msg})
        except:
            msg="Email Not Regiseterd"
            return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def logout(request):
    try:    
        del request.session['email']
        del request.session['fname']
        return render(request,'login.html')
    except:
        return render(request,'login.html')

def change_password(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        if user.password==request.POST['old-password']:
            if request.POST['new-password']==request.POST['cnew-password']:
                user.password=request.POST['new-password']
                user.save()
                return redirect ('logout')
            else:
                msg="New password & Confirm New Password Does Not Matched"
                if user.usertype=="buyer":
                     return render(request,'change-password.html',{'msg':msg})
                else:
                     return render(request,'seller-change-password.html',{'msg':msg})

        else:
            msg="Old Password Does Not Matched"
            if user.usertype=="buyer":
                return render(request,'change-password.html',{'msg':msg})
            else:
                return render(request,'seller-change-password.html',{'msg':msg})

    else:
        if user.usertype=="buyer":
            return render(request,'change-password.html')    
        else:
            return render(request,"seller-change-password.html")
        

def forgot_password(request):
    if request.method=="POST":
        try:
            user = User.objects.get(mobile=request.POST['mobile'])
            mobile =request.POST['mobile']
            otp = random.randint(1000,9999)
            url = "https://www.fast2sms.com/dev/bulkV2"
            
            querystring = {"authorization":"imuAbx2onZYcWRdGJ7w0jM8kTDOLf9EeV1gXS3atK5UQ4zrlPC1VDTtK3b5BfXrSa9ykqJz8cdMlYpNn","variables_values":"str(otp)","route":"otp","numbers":str(mobile)}
            headers = {
                'cache-control': "no-cache"
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
            
            print(response.text)
            return render(request,'otp.html',{'otp':otp,'mobile':user.mobile})
        except:
            msg="mobile Not Registerd"
            return render(request,'forgot-password.html',{'msg':msg})
    else:
        return render(request,'forgot-password.html')
    
def verify_otp(request):
    mobile=request.POST['mobile']
    otp=request.POST['otp']
    uotp=request.POST['uotp']

    if otp==uotp:
        return render(request,'new-password.html',{'mobile':mobile})
    else:
        msg="Invaild OTP"
        return render(request,'otp.html',{'otp':otp,'mobile':mobile,'msg':msg})
        
    
def new_password(request):
    mobile=request.POST['mobile']
    np=request.POST['new-password']
    cnp=request.POST['cnew-password']

    if np==cnp:
        user=User.objects.get(mobile=mobile)
        user.password=np
        user.save()
        msg="Password Updated Successfully"
        return render(request,'login.html')
    else:
        msg="New Password & Confirm New Password Does Not Matched"
        return render(request,'new-password.html',{'mobile':mobile,'msg':msg})




def about(request):
    return render(request,'about.html')


def product_single(request):
    return render(request,'product-single.html')

def blog(request):
    return render(request,'blog.html')


def cart(request):
    return render(request,'cart.html')


def checkout(request):
    return render(request,'checkout.html')


def contact(request):
    return render(request,'contact.html')


def header(request):
    return render(request,'header.html')


def shop(request):
    products=Product.objects.all()
    return render(request,'shop.html',{'products': products})

def seller_add_product(request):
    if request.method=="POST":
        seller=User.objects.get(email=request.session['email'])
        Product.objects.create(
                seller=seller,
                product_category=request.POST['product_category'],
                product_brand=request.POST['product_brand'],
                product_name=request.POST['product_name'],
                product_price=request.POST['product_price'],
                product_size=request.POST['product_size'],
                product_pic=request.FILES['product_pic'],
            )
        msg="Product Added Succsfully"
        return render(request,'seller-add-product.html',{'msg':msg})


    else:
        return render(request,'seller-add-product.html')
    
def seller_view_product(request):
        seller=User.objects.get(email=request.session['email'])
        products=Product.objects.filter(seller=seller)
        return render(request,'seller-view-product.html',{'products':products})

def seller_formal_shoes(request):
        seller=User.objects.get(email=request.session['email'])
        products=Product.objects.filter(seller=seller,product_category="Formal")
        return render(request,'seller-view-product.html',{'products':products})

def seller_sports_shoes(request):
        seller=User.objects.get(email=request.session['email'])
        products=Product.objects.filter(seller=seller,product_category="Sports")
        return render(request,'seller-view-product.html',{'products':products})
    
def seller_casual_shoes(request):
        seller=User.objects.get(email=request.session['email'])
        products=Product.objects.filter(seller=seller,product_category="Casual")
        return render(request,'seller-view-product.html',{'products':products})


def seller_all_shoes(request):
        seller=User.objects.get(email=request.session['email'])
        products=Product.objects.filter(seller=seller)
        return render(request,'seller-view-product.html',{'products':products})

def seller_product_details(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'seller-product-details.html',{'product':product})   


def seller_product_edit(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=="POST" :
        product.product_category=request.POST['product_category']
        product.product_brand=request.POST['product_brand']
        product.product_name=request.POST['product_name']
        product.product_price=request.POST['product_price']
        product.product_size=request.POST['product_size']
        try:
            product.product_pic=request.FILES['product_pic']
        except:
            pass
        product.save()
        msg="Product Updated Succesfully"
        return render(request,'seller-product-edit.html',{'product':product,'msg':msg})
    else:
        return render(request,'seller-product-edit.html',{'product':product})
    
def seller_product_delete(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    msg="Product Deleted Successfully"
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    return render(request,'seller-view-product.html',{'products':products,'msg':msg})

def product_details(request,pk):
    wishlist_flag = False
    cart_flag = False
    user = User.objects.get(email=request.session['email'])
    product = Product.objects.get(pk=pk)
    try:
        Wishlist.objects.get(user=user,product=product,payment_status=False
        )
        wishlist_flag = True
    except:
        pass

    try:
        Cart.objects.get(user=user,product=product)
        cart_flag = True
    except:
        pass
    return render(request, 'product-details.html', {'product': product, 'wishlist_flag': wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.create(user=user,product=product) 
    return redirect('wishlist')

def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlist=Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlist)
    return render(request,'wishlist.html',{'wishlist':wishlist})

def remove_from_wishlist(request,pk):
     product=Product.objects.get(pk=pk)
     user=User.objects.get(email=request.session['email'])
     wishlist=Wishlist.objects.filter(user=user,product=product)
     wishlist.delete()
     return redirect('wishlist')


def add_to_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Cart.objects.create(
        user=user,
        product=product,
        product_price=product.product_price,
        product_qty=1,
        total_price=product.product_price,
        payment_status=False
        ) 
    return redirect('cart')

def cart(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    cart=Cart.objects.filter(user=user,payment_status=False)
    for i in cart:
        net_price=net_price+i.total_price
    request.session['cart_count']=len(cart)
    return render(request,'cart.html',{'cart':cart,'net_price':net_price})

def remove_from_cart(request,pk):
     product=Product.objects.get(pk=pk)
     user=User.objects.get(email=request.session['email'])
     cart=Cart.objects.filter(user=user,product=product)
     cart.delete()
     return redirect('cart')

def change_qty(request):
    cid=int(request.POST['cid'])
    product_qty=int(request.POST['product_qty'])
    cart=Cart.objects.get(pk=cid)
    product_price=cart.product.product_price
    cart.total_price=product_price*product_qty
    cart.product_qty=product_qty
    cart.save()
    return redirect('cart')

@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Checkout Session Data',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
		
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})

def seller_order(request):
	seller=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(payment_status=True)
	orders=[]
	for i in carts:
		if i.product.seller==seller:
			orders.append(i)
	print(orders)
	return render(request,'seller-order.html',{'orders':orders})

