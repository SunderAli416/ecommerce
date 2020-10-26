from django.shortcuts import render
from django.contrib import messages
# Create your views here.
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import BankAccount
from store.models import Order, ShippingAddress, OrderItem,Product
import json
import datetime
from django.core.mail import send_mail
# Create your views here.


def overview(request):
    api_urls={
        'verify':'/verify/',
    }
    return JsonResponse(api_urls)





def verify(request):
    print("called")
    transaction_id=int(datetime.datetime.now().timestamp())
    customer=request.user.customer
    data=json.loads(request.body)
    card_number=data['card_number']
    account_name=data['account_name']
    merchant_account=data['merchant_account']
    pincode=data['pincode']
    e_month=int(data['e_month'])
    e_year=int(data['e_year'])
    pk=data['primary_key']
    order, created=Order.objects.get_or_create(id=pk, customer=customer)
    amount=order.get_cart_total
    amount2=amount
    print(str(data))
    customer_account=BankAccount.objects.filter(card_number=card_number, pin_number=pincode, card_holder=account_name,expiry_month=e_month, expiry_year=e_year)
    if customer_account[0].currency!='USD':
            if customer_account[0].currency=='PKR':
                amount2=amount*160
            elif customer_account[0].currency=='EUR':
                amount2=amount/1.18
            elif customer_account[0].currency=='GBP':
                amount2=amount2/1.31
    if(len(customer_account)==0):
        print("customer doesnt exist")
        messages.error(request, "The Card Could Not Be Processsed..Make Sure The Details Are Valid Or If Your Card Is On Hold From The Bank.")
        return JsonResponse('0',safe=False)
    else:
        merchant_account=BankAccount.objects.get(account_no=merchant_account)
        if(customer_account[0].amount<amount2):
            return JsonResponse('2',safe=False)
        customer_account[0].amount=customer_account[0].amount-amount2
        merchant_account.amount=merchant_account.amount+amount
        customer_account[0].save()
        merchant_account.save()
        order.transaction_id=transaction_id
        if order.shipping==True:
            ShippingAddress.objects.create(customer=customer,order=order, address=data['address'], city=data['city'],state=data['state'],zipcode=data['zip'],)
        order.complete=True
        order.save()
        items=OrderItem.objects.filter(order=order)
        email="Order Confirmed for transaction id "+str(transaction_id)+"\nYour order will be delivered soon\n"
        email+="Shipping To: \n"+str(data['address'])+"\n"+str(data['city'])+"\n"+str(data['state'])+"\n"
        email+="Items: \n"
        for item in items:
            email+=str(item.product.name)+" x"+str(item.quantity)+": $"+str(item.product.price)+"\n"
        email+="Total Amount: $"+str(amount)+"\n"
        email+="Thank You Mr "+str(customer.name)+" for buying from us..\n"
        send_mail('Order Confirmed',email,'sunderlaghari416@gmail.com',[customer.email],fail_silently=False,)
        email2=str(amount2)+" "+str(customer_account[0].currency)+" were deducted from your "+str(customer_account[0].card_type)+" Card"
        send_mail('Amount deducted',email2,'sunderlaghari416@gmail.com',[customer.email],fail_silently=False,)
        
        return JsonResponse('1', safe=False)
    return JsonResponse('1',safe=False)
