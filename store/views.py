from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json
import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login, logout as d_logout
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.decorators import login_required
import re
# Create your views here.
@login_required(login_url='store:login')
def store(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, createed=Order.objects.get_or_create(customer=customer, complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0}
        cartItems=order['get_cart_items']

    products=Product.objects.all()
    context={'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

@login_required(login_url='store:login')
def checkout(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, createed=Order.objects.get_or_create(customer=customer, complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
        shipping=order.shipping
    else:
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems=order['get_cart_items']
        shipping=False
    context={'items':items, 'order':order,'cartItems':cartItems, 'shipping':shipping, 'id':order.id}
    return render(request, 'store/checkout.html', context)

@login_required(login_url='store:login')
def cart(request):
    if request.user.is_authenticated:
        customer=request.user.customer
        order, createed=Order.objects.get_or_create(customer=customer, complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0, 'get_cart_items':0}
        cartItems=order['get_cart_items']
    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html',context)


@login_required(login_url='store:login')
def updateItem(request):
    data=json.loads(request.body)
    productId=data['productId']
    action=data['action']
    print('Action:',action)
    print('ID:',productId)
    customer=request.user.customer
    product=Product.objects.get(id=productId)
    order, created=Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created=OrderItem.objects.get_or_create(order=order, product=product)
    if action=='add':
        orderItem.quantity=(orderItem.quantity+1)
    elif action=='remove':
        orderItem.quantity=(orderItem.quantity-1)

    orderItem.save()
    if orderItem.quantity<=0:
        orderItem.delete()
    return JsonResponse('Item added....',safe=False)

@login_required(login_url='store:login')
def processOrder(request):
    transaction_id=int(datetime.datetime.now().timestamp())
    data=json.loads(request.body)
    if request.user.is_authenticated:
        customer=request.user.customer
        order, created=Order.objects.get_or_create(customer=customer, complete=False)
        total=float(data['form']['total'])
        order.transaction_id=transaction_id
        if total==order.get_cart_total:
            order.complete=True
        order.save()

        if order.shipping==True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
            email="Order Confirmed for transaction id "+str(transaction_id)+"\nYour order will be delivered soon\n"
            email+="Shipping To: \n"+str(data['shipping']['address'])+"\n"+str(data['shipping']['city'])+"\n"+str(data['shipping']['state'])+"\n"
            email+="Total Amount: $"+str(total)+"\n                 "
            email+="Thank You Mr "+str(customer.name)+" for buying from us..\n"
            send_mail(
            'Order Confirmed',
            email,
            'sunderlaghari416@gmail.com',
            [customer.email],
            fail_silently=False,)

            print("Reached here")

    else:
        print("Not logged")
    return JsonResponse('Order processed...',safe=False)

@login_required(login_url='store:login')
def payment(request,pk):
    customer=request.user.customer
    cart=Order.objects.filter(id=pk, complete=False, customer=customer)
    if(len(cart)==0):
        return redirect('store:store')
    else:
        amount=cart[0].get_cart_total
        shipping=cart[0].shipping
        num=cart[0].get_cart_items
    
    context={'pk':pk, 'amount':amount, 'cartItems':num, 'shipping':shipping}
    return render(request, 'store/payment_form.html', context)


def login(request):
    if request.user.is_authenticated:
        return redirect('store:store')
    else:
        if request.method=='POST':
            username=request.POST.get('username')
            password=request.POST.get('password')

            user=authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('store:store')
            else:
                messages.info(request, "Username or password is incorrect")
    return render(request, 'store/login.html')

def register(request):
     passFlag=0
     usernameFlag=0
     emailFlag=0
     phoneFlag=0
     nameFlag=0
     emailRegex='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
     nameRegex='^[a-zA-Z ]+$'
     phoneRegex='\w{3}-\w{3}-\w{4}'
     usernameRegex='^[a-zA-Z0-9_.-]+$'
     if request.user.is_authenticated:
        return redirect('store:store')
     else:
        if request.method=='POST':
            username=request.POST.get('username')
            name=request.POST.get('name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')
            password=request.POST.get('password')
            usernames=User.objects.filter(username=username)
            if(re.search(emailRegex,email)):
                emailFlag=1
            else:
                messages.info(request, "Invalid email")

            if(re.search(nameRegex,name)):
                nameFlag=1
            else:
                messages.info(request, "inavlid name")

            if(re.search(usernameRegex,username)):
                usernameFlag=1
                if(len(usernames)==1):
                    usernameFlag=0
                    messages.info(request, "Username Already exists")
            else:
                messages.info(request,'Invalid Username')
            
            if(re.search(phoneRegex,phone)):
                phoneFlag=1
            else:
                messages.info(request, 'Invalid Phone Number')
                messages.info(request, 'xxx-xxx-xxxx')




            if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
                passFlag=1
            else:
                messages.info(request, "Password Should only contain\nuppercase letters: A-Z\nlowercase letters: a-z\nnumbers: 0-9\nany of the special characters: @#$%^&+=\n")
            
            if passFlag==1 and usernameFlag==1 and emailFlag==1 and phoneFlag==1 and nameFlag==1:
                user=User.objects.create(username=username, email=email)
                user.set_password(password)
                user.save()
                customer=Customer(user=user, name=name, phone=phone, email=email)
                customer.save()
                return redirect('store:login')
     return render(request, 'store/registration.html')
    


def logout(request):
    d_logout(request)
    return redirect('store:login')