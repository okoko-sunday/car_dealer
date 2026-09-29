def tenant(request):
    return {"dealer": getattr(request, "dealer", None)}
