import requests
from django.shortcuts import render

def show_orders(request):
    api_url = "http://127.0.0.1:8000/api/order/"
    context = {}

    if request.method == 'POST':
        if 'pickup' in request.POST:
            order_id = request.POST.get('pickup')

            # Get a specific order
            try:
                response = requests.get(api_url + "order/" + str(order_id))
                response.raise_for_status()
                order = response.json()

                # Create log
                try:
                    response = requests.post(api_url + "order/" + str(order_id) + "/orderlogs/", json={'incident': 'Order completed'})
                    response.raise_for_status()
                    print("Order log created successfully:", response.json())
                except requests.RequestException as e:
                    print(f"Error logging order incident: {e}")
            except requests.RequestException as e:
                print(f"Error fetching data from API: {e}")
                order = []  # Fallback to an empty list if the API call fails
            
            # Update the order to be completed
            try:
                data = {'order_status': 'Completed'}
                response = requests.patch(api_url + str(order_id) + "/", data=data)
                response.raise_for_status()
                order = response.json()
                print("Order updated successfully")
                # One could implement the mailing system here
                context['message'] = "Mail receipt sent to " + order['order']['customer_name']
                print("Mail receipt sent to " + order['order']['customer_name'])
            except requests.RequestException as e:
                print(f"Error updating order line in API: {e}")

        elif 'delete' in request.POST:
            order_id = request.POST['delete']
            print(f"Deleting order with ID: {order_id}")
            try:
                response = requests.delete(api_url + request.POST['delete'] + "/")
                if response.status_code == 204:
                    print("Order deleted successfully")
                    context['message'] = "Order deleted successfully"
                else:
                    print("Failed to delete order")
                    context['message'] = "Failed to delete order"
            except requests.RequestException as e:
                print(f"Error making DELETE request: {e}")
                context['message'] = "Error deleting order"
        elif 'generate' in request.POST:
            try:
                response = requests.post(api_url)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Error creating order in API: {e}")
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        orders = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        orders = []  # Fallback to an empty list if the API call fails
    context['orders'] = orders

    return render(request, 'LocationModule/index.html', context)

def show_order(request):
    api_url = "http://127.0.0.1:8000/api/"
    context = {}

    if request.method == 'POST':
        order_id = request.POST.get('details')
        if 'receive' in request.POST:
            order_line_id = request.POST.get('receive')

            # Get a specific order
            try:
                response = requests.get(api_url + "order/" + str(order_id))
                response.raise_for_status()
                order = response.json()
            except requests.RequestException as e:
                print(f"Error fetching data from API: {e}")
                order = {}  # Fallback to an empty list if the API call fails
            context['order'] = order

            # Update the order line to be received
            try:
                data = {'order_line_status': 'Received'}
                response = requests.patch(api_url + "order/" + str(order_id) + "/orderlines/" + str(order_line_id), data=data)
                response.raise_for_status()
                print("Order line updated successfully")

                # Create log
                try:
                    response = requests.post(api_url + "order/" + str(order_id) + "/orderlogs/", json={'incident': str(order_line_id) + ' received'})
                    response.raise_for_status()
                    print("Order log created successfully:", response.json())
                except requests.RequestException as e:
                    print(f"Error logging order incident: {e}")
            except requests.RequestException as e:
                print(f"Error updating order line in API: {e}")
    else:
        order_id = request.GET.get('details')
        # Get a specific order
        try:
            response = requests.get(api_url + "order/" + str(order_id))
            response.raise_for_status()
            order = response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from API: {e}")
            order = {}  # Fallback to an empty list if the API call fails
        context['order'] = order

    # Get all related order lines
    try:
        response = requests.get(api_url + "order/" + str(order_id) + "/orderlines/")
        response.raise_for_status()
        order_lines = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        order_lines = []  # Fallback to an empty list if the API call fails
    context['order_lines'] = order_lines
    print(order)
    # Check if all the order statuses are received and ready
    all_received = all(order_line['order_line_status'] == 'Received' for order_line in order_lines)
    order_ready_or_completed = order['order_status'] in ['Ready', 'Completed']
    if all_received and not order_ready_or_completed:
        print("updating overall order")
        # Update the order to be ready
        try:
            data = {'order_status': 'Ready'}
            response = requests.patch(api_url + "order/" + str(order_id) + "/", data=data)
            response.raise_for_status()
            context['order']['order_status'] = 'Ready'
            print("Order updated successfully")
            # One could implement the mailing system here
            context['message'] = "Mail sent to " + order['customer_name']
            print("Mail sent to " + order['customer_name'])
        except requests.RequestException as e:
            print(f"Error updating order in API: {e}")

    # Get all related order logs
    try:
        response = requests.get(api_url+ "order/" + str(order_id) + "/orderlogs/")
        response.raise_for_status()
        order_logs = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        order_logs = []  # Fallback to an empty list if the API call fails
    context['order_logs'] = order_logs

    return render(request, 'LocationModule/order-details.html', context)