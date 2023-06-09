from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from store.models import *
import random

@login_required(login_url='dangNhap')
def index(request):
    categories = Category.objects.filter(status=0)
    cartLength = Cart.objects.count()
    wishListLength = Wishlist.objects.count()
    rawCart = Cart.objects.filter(user=request.user)
    for item in rawCart:
        if item.product_qty > item.product.quantity:
            Cart.objects.delete(id = item.id)

    cartItems = Cart.objects.filter(user=request.user)
    total_price = 0
    for item in cartItems:
        total_price = total_price + item.product.selling_price * item.product_qty
    
    userprofile = Profile.objects.filter(user=request.user).first()

    context = {'cartItems': cartItems, 'total_price': total_price, 'categories': categories, 'userprofile': userprofile, 'cartLength': cartLength, 'wishListLength': wishListLength}
    return render(request, 'store/thanhtoan.html', context)

@login_required(login_url='dangNhap')
def datHang(request):
    if request.method == "POST":

        currentUser = User.objects.filter(id=request.user.id).first()

        if not currentUser.first_name:
            currentUser.first_name = request.POST.get('fname')
            currentUser.last_name = request.POST.get('lname')
            currentUser.save()

        if not Profile.objects.filter(user=request.user):
            userprofile = Profile()
            userprofile.user = request.user
            userprofile.phone = request.POST.get('phone')
            userprofile.address = request.POST.get('address')
            userprofile.city = request.POST.get('city')
            userprofile.state = request.POST.get('state')
            userprofile.country = request.POST.get('country')
            userprofile.zipcode = request.POST.get('zipcode')
            userprofile.save()

        neworder = Order()
        neworder.user = request.user
        neworder.fname = request.POST.get('fname')
        neworder.lname = request.POST.get('lname')
        neworder.email = request.POST.get('email')
        neworder.phone = request.POST.get('phone')
        neworder.address = request.POST.get('address')
        neworder.city = request.POST.get('city')
        neworder.state = request.POST.get('state')
        neworder.country = request.POST.get('country')
        neworder.zipcode = request.POST.get('zipcode')
        neworder.payment_mode = request.POST.get('payment_mode')

        carts = Cart.objects.filter(user=request.user)
        cart_total_price = 0
        for item in carts:
            cart_total_price = cart_total_price + item.product.selling_price * item.product_qty

        neworder.total_price = cart_total_price

        trackno = 'foodhub'+str(random.randint(11111111, 99999999))
        while Order.objects.filter(tracking_no=trackno) is None:
            trackno = 'foodhub'+str(random.randint(11111111, 99999999))
        
        neworder.tracking_no = trackno
        neworder.save()

        neworderitems = Cart.objects.filter(user=request.user)
        for item in neworderitems:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )

            orderproduct = Product.objects.filter(id=item.product_id).first()
            orderproduct.quantity = orderproduct.quantity - item.product_qty
            orderproduct.save()
        
        Cart.objects.filter(user=request.user).delete()
        messages.success(request, "Đặt hàng thành công!")

    return redirect('/')