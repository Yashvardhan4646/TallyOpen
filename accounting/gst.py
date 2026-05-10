def calculate_gst(amount, gst_percent):

    gst_amount = (amount * gst_percent) / 100

    final_amount = amount + gst_amount

    return {
        "original": amount,
        "gst": gst_amount,
        "total": final_amount
    }