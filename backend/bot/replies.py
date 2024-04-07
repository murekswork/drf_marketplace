class Replies:
    COURIER_PROFILE_INFO = """
    Courier Information:
    - <b>ID:</b> {id}
    - <b>Username:</b> {username}
    - <b>First Name:</b> {first_name}
    - <b>Last Name:</b> {last_name}
    - <b>Location:</b> {location}
    - <b>Busy:</b> {busy} 🚶‍♂️
    - <b>Current Delivery ID:</b> {current_delivery_id} 📦
    - <b>Done Deliveries:</b> {done_deliveries} ✅
    - <b>Balance:</b> {balance} 💰
    - <b>Rank:</b> {rank} 🏆
    """

    DELIVERY_INFO = """
    <b>Hey! You have received a new delivery </b>
    <b>You have {minutes} minutes to bring it to client! Hurry up </b>
    <b>🚚 Your delivery info 📦</b>
    <b>amount:</b> {amount} 💰
    <b>status:</b> {status} ℹ️
    <b>address:</b> {address} 🏠
    <b>estimated_time:</b> {estimated_time} 🕒"""

    COURIER_START_CARRYING_INFO = (
        "<b>Send your LIVE location now, so i will check for orders beside you!📍</b>"
    )

    COURIER_SENT_LOCATION_INFO = "<b>Successfully received location and added you to line. Stay tuned for deliveries!🚴</b>"

    PICKED_UP_DELIVERY_INFO = (
        "Nice job! Now you should bring picked up goods to client in location below"
    )

    PICKUP_MSG_INFO = "You should pick up goods on point on to from this msg"

    CLOSED_DELIVERY_INFO = "Delivery closed with status {}!"

    STOP_CARRYING_INFO = "Your work is over, thanks! See you next time!"

    CURRENT_DELIVERY_INFO = "Your current delivery is {}"

    DELIVERY_TAKING_LATE_NOTIFICATION = "🚴 You should hurry up! You current delivery: {} should be bringed in {} minutes!"

    DELIVERY_TIME_OUT_NOTIFICATION = "🕒 Your delivery time is over! Now you have to bring package in 5 minutes, otherwise we will have to fine you!"

    DELIVERY_CANCELLED_BY_CONSUMER_NOTIFICATION = (
        " Unfortunately your delivery was cancelled by consumer!"
    )

    DELIVERY_COURIER_NOT_ON_REQUIRED_POINT_ANSWER = "You cant mark your delivery as picked up or delivered because you are not on required location!"