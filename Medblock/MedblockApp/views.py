from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import Manufacturer, Distributor, Retailer, Customer, Product, Unit, Shipment, Block
from django.contrib.auth.hashers import make_password, check_password
import json
from datetime import datetime, UTC, timezone
# Utility functions
import hashlib
from hashlib import sha256
from django.utils import timezone
from django.db.models import Q

import uuid

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'dist_home.html')
# Manufacturer Views
def register_manufacturer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        reg_no = request.POST.get('reg_no')
        email = request.POST.get("email")
        raw_password = request.POST.get('password')
        if Manufacturer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register_manufacturer')
        
        manufacturer = Manufacturer(name=name, address=address, reg_no=reg_no, email=email)
        manufacturer.set_password(raw_password)
        manufacturer.save()
        return redirect('mf_login')
    return render(request, 'register_manufacturer.html')

def mf_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            manufacturer = Manufacturer.objects.get(email=email)
        except Manufacturer.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('mf_login')

        if manufacturer.check_password(password):
            request.session["email"] = email
            request.session["id"] = manufacturer.id
            request.session["name"] = manufacturer.name
            messages.success(request, 'Login successful.')
            return redirect('mf_home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('mf_login')

    return render(request, 'mf_login.html')

def logout_manufacturer(request):
    if 'id' in request.session:
        del request.session['id']
        del request.session['email']
        del request.session['name']
        messages.success(request, 'Logged out successfully.')
    return redirect('home')

def mf_home(request):
    return render(request, 'mf_home.html')

def add_products(request):
    if 'id' not in request.session:
        return redirect('mf_login')
    
    if request.method == 'POST':
        name = request.POST.get('p_name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        photo = request.FILES.get('photo')
        manufacturer_id = request.session.get('id')
        manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)
        
        if name and price:
            Product.objects.create(
                name=name, 
                manufacturer=manufacturer, 
                price=price, 
                description=description,
                photo=photo
            )
            messages.success(request, 'Product added successfully.')
            return redirect('add_products')

    products = Product.objects.filter(manufacturer__id=request.session.get('id'))
    return render(request, 'products.html', {'products': products})

def add_units(request):
    if 'id' not in request.session:
        return redirect('mf_login')
    
    if request.method == 'POST':
        product_id = request.POST.get('unit')
        quantity = int(request.POST.get('quantity'))
        expiration_date = request.POST.get('e_date')
        product = get_object_or_404(Product, id=product_id)
        manufacturer_id = request.session.get('id')
        manufacturer = get_object_or_404(Manufacturer, id=manufacturer_id)

        for _ in range(quantity):
            unit = Unit(product=product, e_date=expiration_date)
            unit.save()
            unit.refresh_from_db()
            # Prepare the block data
            block_data = {
                'unit_id': unit.id,
                'product_id': unit.product.id,
                'action': "Manufactured",
                'manufacturer_id' : request.session["id"],
                'timestamp': datetime.now(UTC).isoformat(), 
                'expiry':expiration_date
            }
            create_blockchain_entry(block_data)

        messages.success(request, 'Units added and blockchain updated.')
        return redirect('add_units')

    products = Product.objects.filter(manufacturer__id=request.session.get('id'))
    return render(request, 'add_units.html', {'products': products})



def mf_shipments(request):
    if 'id' not in request.session:
        return redirect('mf_login')
    
    if request.method == 'POST':
        # Get the selected quantity from the form
        quantity = int(request.POST.get('quantity', 0))
        shipment_date = request.POST.get('shipment_date')
        distributor_id = request.POST.get('d_name')
        retailer_id = request.POST.get('retailer')
        tracking_number = uuid.uuid4()

        if quantity <= 0:
            messages.error(request, 'Please select a valid quantity.')
            return redirect('mf_shipments')

        # Get distributor and retailer based on IDs
        distributor = get_object_or_404(Distributor, id=distributor_id) if distributor_id else None
        retailer = get_object_or_404(Retailer, id=retailer_id) if retailer_id else None
        
        # Fetch the first N units (based on the selected quantity) that are available
# Get all units that are not part of any shipment
        units = Unit.objects.exclude(shipments__isnull=False)[:quantity]
        
        if not units.exists():
            messages.error(request, 'No units available.')
            return redirect('mf_shipments')

        # Create a shipment entry
        shipment = Shipment(
            shipment_date=shipment_date,
            status='intransit_distributor',
            distributor=distributor,
            retailer=retailer,
            tracking_number=tracking_number
        )
        shipment.save()

        # Attach the selected units to the shipment
        shipment.units.set(units)

        # Update the blockchain for each unit in the shipment
        for unit in units:
            block_data = {
                "unit_id": unit.id,
                "action": "Shipment to distributor",
                "distributor_id": distributor.id if distributor else None,
                "retailer_id": retailer.id if retailer else None,
                "tracking_number": str(tracking_number),
                "shipment_date": shipment_date
                
            }
            try:
                create_blockchain_entry(block_data)
            except Exception as e:
                messages.error(request, f'Error adding unit {unit.id} to blockchain: {str(e)}')

        # Provide feedback on success
        messages.success(request, 'Shipment created and added to blockchain successfully.')
        return redirect('mf_shipments')
    
    # Load units, distributors, and retailers to display in the form
    units = Unit.objects.exclude(shipments__isnull=False)
    distributors = Distributor.objects.all()
    retailers = Retailer.objects.all()
    products = Product.objects.filter(id__in=units.values('product')).distinct()
    product_data = []
    for product in products:
        product_units_count = units.filter(product=product).count()
        product_data.append({
            'id': product.id,
            'name': product.name,
            'units_count': product_units_count
        })

    return render(request, 'mf_shipments.html', {'units': units, 'distributors': distributors, 'products': product_data})


def update_blockchain_for_shipment(shipment):
    # Prepare block data with shipment information
    block_data = {
        'shipment_id': shipment.id,
        'units': [unit.id for unit in shipment.units.all()],  # List of unit IDs
        'action': 'shipped',
        'distributor_id': shipment.distributor.id if shipment.distributor else None,
        'retailer_id': shipment.retailer.id if shipment.retailer else None,
        'tracking_number': shipment.tracking_number,
        'status': shipment.status,
        'timestamp': datetime.now(UTC).isoformat()  # Use UTC timestamp
    }

    # Get the last block (previous block)
    previous_block = Block.objects.last()
    previous_hash = previous_block.hash if previous_block else '0'
    previous_proof = previous_block.proof if previous_block else 0

    # Find proof using proof of work algorithm
    proof = proof_of_work(previous_proof)

    # Create new block
    block = Block(
        index=(previous_block.index + 1 if previous_block else 1),
        timestamp=datetime.now(UTC),  # Use UTC timestamp for consistency
        previous_hash=previous_hash,
        proof=proof,
        data=json.dumps(block_data, sort_keys=True)  # Serialize block data
    )

    # Compute the block's hash
    block.hash = block.compute_hash()
    
    # Save the block to the blockchain (database)
    block.save()

def mf_track(request):
    if 'id' not in request.session:
        return redirect('mf_login')
    
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            return render(request, 'shipment_detail.html', {'shipment': shipment})
        except Shipment.DoesNotExist:
            messages.error(request, 'Shipment not found.')
            return redirect('mf_track')

    return render(request, 'mf_track.html')

# Distributor Views
def register_distributor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get("email")
        raw_password = request.POST.get('password')
        if Distributor.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register_distributor')
        
        distributor = Distributor(name=name, address=address, email=email)
        distributor.set_password(raw_password)
        distributor.save()
        return redirect('dist_login')
    return render(request, 'dist_reg.html')

def dist_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            distributor = Distributor.objects.get(email=email)
        except Distributor.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('dist_login')

        if distributor.check_password(password):
            request.session["email"] = email
            request.session["id"] = distributor.id
            request.session["name"] = distributor.name
            messages.success(request, 'Login successful.')
            return redirect('dist_home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('dist_login')

    return render(request, 'dist_login.html')

def logout_distributor(request):
    if 'id' in request.session:
        del request.session['id']
        del request.session['email']
        del request.session['name']
        messages.success(request, 'Logged out successfully.')
    return redirect('home')

def dist_home(request):
    return render(request, 'dist_home.html')

def dist_products(request):
    if 'id' not in request.session:
        return redirect('dist_login')
    
    distributor_id = request.session.get('id')
    shipments = Shipment.objects.filter(distributor__id=distributor_id, status='intransit_distributor')
    return render(request, 'dist_products.html', {'shipments': shipments})

def mark_received(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if 'id' not in request.session:
        return redirect('dist_login')

    if request.method == 'POST':
        shipment.status = 'distributor_received'
        shipment.save()
        update_blockchain_for_shipment(shipment)
        messages.success(request, 'Shipment marked as received.')
        return redirect('dist_products')

    return render(request, 'mark_received.html', {'shipment': shipment})

def verify_product(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    
    return render(request, 'verify_product.html', {'shipment': shipment})

def dist_shipments(request):
    if 'id' not in request.session:
        return redirect('dist_login')  # Redirect to distributor login if not logged in
    
    distributor = get_object_or_404(Distributor, id=int(request.session['id']))
    if request.method == 'POST':
        # Get the selected quantity from the form
        quantity = int(request.POST.get('quantity', 0))
        shipment_date = request.POST.get('shipment_date')
        retailer_id = request.POST.get('retailer')  # Get retailer ID from the form
        tracking_number = uuid.uuid4()  # Generate a unique tracking number

        if quantity <= 0:
            messages.error(request, 'Please select a valid quantity.')
            return redirect('dist_shipments')
        

        
        
        retailer = get_object_or_404(Retailer, id=retailer_id) if retailer_id else None
        
        # Fetch the first N units (based on the selected quantity) that are available
        units = Unit.objects.filter(
                                    shipments__distributor=distributor,
                                    shipments__status='distributor_received'
                                ).exclude(
                                    shipments__status__in=[
                                        'intransit_distributor', 
                                        'intransit_retailer', 
                                        'retailer_received', 
                                        'sold'
                                    ]
                                ).distinct()[:quantity]
        
        if not units.exists():
            messages.error(request, 'No units available.')
            return redirect('dist_shipments')

        # Create a shipment entry
        shipment = Shipment(
            shipment_date=shipment_date,
            status='intransit_retailer',  # Update status for retailer shipment
            distributor=distributor,
            retailer=retailer,
            tracking_number=tracking_number
        )
        shipment.save()

        # Attach the selected units to the shipment
        shipment.units.set(units)

        # Update the blockchain for each unit in the shipment
        for unit in units:
            block_data = {
                "unit_id": unit.id,
                "action": "Shipment to retailer",
                "distributor_id": distributor.id if distributor else None,
                "retailer_id": retailer.id if retailer else None,
                "tracking_number": str(tracking_number),
                "shipment_date": shipment_date
            }
            try:
                create_blockchain_entry(block_data)
            except Exception as e:
                messages.error(request, f'Error adding unit {unit.id} to blockchain: {str(e)}')

        # Provide feedback on success
        messages.success(request, 'Shipment created and added to blockchain successfully.')
        return redirect('dist_shipments')
    
    # Load units, distributors, and retailers to display in the form
    units = Unit.objects.filter(
                                    shipments__distributor=distributor,
                                    shipments__status='distributor_received'
                                ).exclude(
                                    shipments__status__in=[
                                        'intransit_distributor', 
                                        'intransit_retailer', 
                                        'retailer_received', 
                                        'sold'
                                    ]
                                ).distinct()
    retailers = Retailer.objects.all()
    products = Product.objects.filter(id__in=units.values('product')).distinct()
    product_data = []
    for product in products:
        product_units_count = units.filter(product=product).count()
        product_data.append({
            'id': product.id,
            'name': product.name,
            'units_count': product_units_count
        })

    return render(request, 'dist_shipments.html', {'units': units, 'retailers': retailers, 'products': product_data})

# Retailer Views
def register_retailer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        email = request.POST.get("email")
        raw_password = request.POST.get('password')
        if Retailer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register_retailer')
        
        retailer = Retailer(name=name, address=address, email=email)
        retailer.set_password(raw_password)
        retailer.save()
        return redirect('ret_login')
    return render(request, 'ret_reg.html')

def ret_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            retailer = Retailer.objects.get(email=email)
        except Retailer.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('ret_login')

        if retailer.check_password(password):
            request.session["email"] = email
            request.session["id"] = retailer.id
            request.session["name"] = retailer.name
            messages.success(request, 'Login successful.')
            return redirect('ret_home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('ret_login')

    return render(request, 'ret_login.html')

def logout(request):
    if 'id' in request.session:
        del request.session['id']
        del request.session['email']
        del request.session['name']
        messages.success(request, 'Logged out successfully.')
    return redirect('home')

def ret_home(request):
    return render(request, 'ret_home.html')

def ret_products(request):
    if 'id' not in request.session:
        return redirect('ret_login')
    
    retailer_id = request.session.get('id')
    shipments = Shipment.objects.filter(retailer__id=retailer_id, status='intransit_retailer')
    return render(request, 'ret_products.html', {'shipments': shipments})

def mark_received_retailer(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    if 'id' not in request.session:
        return redirect('ret_login')

    if request.method == 'POST':
        shipment.status = 'retailer_received'
        shipment.save()
        update_blockchain_for_shipment(shipment)
        messages.success(request, 'Shipment marked as received.')
        return redirect('ret_products')

    return render(request, 'mark_received_retailer.html', {'shipment': shipment})

def verify_product_retailer(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    # Implement product verification using blockchain
    return render(request, 'verify_product_retailer.html', {'shipment': shipment})

def ret_sales(request):
    if 'id' not in request.session:
        return redirect('ret_login')
    
    units = Unit.objects.filter(shipments__status='retailer_received').exclude(shipments__status='sold')

    product_data = []

    # Group available units by product and pass them to the template
    for product in Product.objects.filter(id__in=units.values('product').distinct()):
        available_units = units.filter(product=product)
        product_data.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'units': [{'unit_id': unit.id} for unit in available_units]  # List of available unit IDs
        })
    
    if request.method == 'POST':
        retailer_id = request.session['id']
        cust_email = request.POST.get('cust_email')
        selected_units = json.loads(request.POST.get('selected_units', '[]'))
        tracking_number = uuid.uuid4()

        if not selected_units or len(selected_units) == 0:
            messages.error(request, 'Please select or scan at least one unit.')
            return redirect('ret_sales')

        retailer = get_object_or_404(Retailer, id=retailer_id) if retailer_id else None
        customer = Customer.objects.filter(email=cust_email).first() if cust_email else None
        shipment_date = timezone.now().date()

        # Create the shipment record
        shipment = Shipment(
            shipment_date=shipment_date,
            status='sold',
            retailer=retailer,
            customer=customer,
            tracking_number=tracking_number
        )
        shipment.save()

        total_price = 0
        bill_items = {}

        # Process selected units
        units = Unit.objects.filter(id__in=selected_units, shipments__status='retailer_received')
        sold_units = Unit.objects.filter(id__in=selected_units, shipments__status='sold')

        if sold_units.exists():
            # Condition if any of the selected units are already sold
            messages.error(request, 'Some of the selected units are already sold.')
            return redirect('ret_sales')

        if not units.exists():
            messages.error(request, 'No valid units were selected.')
            return redirect('ret_sales')

        # Add selected units to the shipment and calculate prices
        for unit in units:
            product = unit.product  # Get the product associated with the unit
            price = product.price

            # Add the unit to the shipment
            shipment.units.add(unit)

            # Calculate total price for the selected units
            total_price += price

            # Add the product to the bill or update quantity if it's already there
            if product.id not in bill_items:
                bill_items[product.id] = {
                    "item_name": product.name,
                    "quantity": 1,  # Starts with 1 unit
                    "price": price,
                    "total": price
                }
            else:
                # If product already exists in the bill, update its quantity and total
                bill_items[product.id]["quantity"] += 1
                bill_items[product.id]["total"] += price

            # Blockchain update for each unit
            block_data = {
                "unit_id": unit.id,
                "action": "Sold",
                "customer_id": customer.id if customer else None,
                "retailer_id": retailer.id if retailer else None,
                "tracking_number": str(tracking_number),
                "shipment_date": shipment_date.strftime('%Y-%m-%d')
            }
            try:
                create_blockchain_entry(block_data)
            except Exception as e:
                messages.error(request, f'Error adding unit {unit.id} to blockchain: {str(e)}')
                raise e

        # Generate bill data
        bill_data = {
            "tracking_number": tracking_number,
            "retailer_name": retailer.name,
            "retailer_email": retailer.email,
            "customer_email": cust_email,
            "total_price": total_price,
            "items": list(bill_items.values()),  # Convert bill_items dict to list for rendering
        }

        messages.success(request, 'Shipment created and added to blockchain successfully.')



        return render(request, 'ret_sales.html', {'bill': bill_data, 'products': product_data})

    # Handle GET request
    

    return render(request, 'ret_sales.html', {'products': product_data})

# Customer Views
def register_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get("email")
        raw_password = request.POST.get('password')
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register_customer')
        
        customer = Customer(name=name, email=email)
        customer.set_password(raw_password)
        customer.save()
        return redirect('cust_login')
    return render(request, 'customer_reg.html')

def cust_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('cust_login')

        if customer.check_password(password):
            request.session["email"] = email
            request.session["id"] = customer.id
            request.session["name"] = customer.name
            messages.success(request, 'Login successful.')
            return redirect('cust_home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('cust_login')

    return render(request, 'cust_login.html')

def logout_customer(request):
    if 'id' in request.session:
        del request.session['id']
        del request.session['email']
        del request.session['name']
        messages.success(request, 'Logged out successfully.')
    return redirect('home')

def cust_home(request):
    if 'id' not in request.session:
        return redirect('cust_login')
    return render(request, 'cust_home.html')

def purchase_history(request):
    if 'id' not in request.session:
        return redirect('cust_login')
    
    user_id = request.session['id']
    

    # Filter the Shipment table for 'sold' status and the current user as the customer
    sold_shipments = Shipment.objects.filter(status='sold', customer=user_id)

    # Prepare the data for rendering
    purchase_history_data = []
    for shipment in sold_shipments:
        purchase_history_data.append({
            'tracking_number': shipment.tracking_number,
            'date': shipment.shipment_date,
            'retailer_name': shipment.retailer.name if shipment.retailer else 'N/A',
            'units': [{'unit_id': unit.id, 'product_name': unit.product.name} for unit in shipment.units.all()],
        })

    # Render the purchase history template with the data
    return render(request, 'purchase_history.html', {'purchase_history': purchase_history_data})

def verify_product_customer(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Implement product verification using blockchain
    return render(request, 'verify_product_customer.html', {'product': product})

def proof_of_work(previous_proof):
    proof = 0
    while True:
        guess = f'{proof}{previous_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        if guess_hash[:4] == "0000":  # Adjust the number of leading zeros as needed
            return proof
        proof += 1

def create_blockchain_entry( block_data):
    previous_block = Block.objects.last()
    previous_hash = previous_block.hash if previous_block else '0'
    previous_proof = previous_block.proof if previous_block else 0
    proof = proof_of_work(previous_proof)

    block = Block(
        index=(previous_block.index + 1 if previous_block else 1),
        timestamp=datetime.now(UTC),  # Use UTC timestamp for consistency
        previous_hash=previous_hash,
        proof=proof,
        data=json.dumps(block_data, sort_keys=True)
    )
    
    block.hash = block.compute_hash()  # Compute hash after setting all fields
    block.save()

# Verify the authenticity of a unit based on blockchain data
def verify_unit_authenticity(unit_id):
    blocks = Block.objects.all().order_by('index')
    transaction_history = []
    previous_hash = "0"

    for block in blocks:
        computed_hash = block.compute_hash()
        block.hash = computed_hash
        if block.hash != computed_hash:
            return False, f'Block {block.index} integrity check failed. Origin block: {block.hash}, Computed hash: {computed_hash}', None
        if block.previous_hash != previous_hash:
            return False, "Blockchain chain is broken.", None

        previous_hash = block.hash

        block_data_dict = block.get_data()
        if block_data_dict.get("unit_id") == unit_id:
            transaction_history.append({
                "action": block_data_dict.get("action"),
                "timestamp": block.timestamp,
                "block_index": block.index
            })

    if transaction_history:
        unit = Unit.objects.get(id=unit_id)
        product = unit.product
        manufacturer = product.manufacturer
        unit_data = {
            "unit_id": unit.id,
            "product_name": product.name,
            "manufacturer_name": manufacturer.name,
            "transaction_history": transaction_history
        }
        return True, "Unit is authentic.", unit_data
    else:
        return False, "Unit not found in the blockchain.", None

# Unit verification view
def unit_verification_view(request):
    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')  
        is_authentic, message, unit_data = verify_unit_authenticity(int(unit_id))

        return render(request, 'verification_result.html', {
            'message': message,
            'unit_data': unit_data if is_authentic else None
        })

    return render(request, 'verification_result.html')