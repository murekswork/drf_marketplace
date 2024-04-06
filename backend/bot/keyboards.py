from telegram import KeyboardButton, ReplyKeyboardMarkup


class CourierReplyMarkups:
    GOT_DELIVERY_MARKUP = ReplyKeyboardMarkup(
        [["Show delivery", "Picked up delivery", "Show profile", "Cancel delivery"]],
        one_time_keyboard=False,
    )

    COURIER_MAIN_MARKUP = ReplyKeyboardMarkup(
        [
            [
                "Show profile",
            ]
        ],
        one_time_keyboard=True,
    )

    COURIER_RECEIVE_LOCATION_MARKUP = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "GOT IT!",
                )
            ]
        ],
        one_time_keyboard=True,
    )

    CARRYING_NOT_DELIVERY_MARKUP = ReplyKeyboardMarkup(
        [["Show profile", "Stop carrying"]], one_time_keyboard=True
    )

    NOT_CARRYING_MARKUP = ReplyKeyboardMarkup(
        [["Show profile", "Start carrying"]], one_time_keyboard=True
    )

    PICKED_UP_DELIVERY_MARKUP = ReplyKeyboardMarkup(
        [["Show delivery", "Delivered!", "Show profile"]], one_time_keyboard=False
    )


class CommonMarkups:
    MAIN_MARKUP = ReplyKeyboardMarkup(
        [
            # ['Start carrying', 'Become courier', ]
            [
                "Start carrying",
            ]
        ]
    )
