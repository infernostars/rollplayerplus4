from random import uniform
def lanchester(a, b, ar, br, e):
    if a > b:
        winner, loser = a, b
        retreat = br
    else:
        winner, loser = b, a
        retreat = ar
    ratio = loser/winner
    if a > b:
        return 0, (ratio*retreat**e-ratio+1)**(1/e)*a, retreat*b
    else:
        return 1, retreat*a, (ratio*retreat**e-ratio+1)**(1/e)*b

def casualties(a, b, loss):
    if loss is None:
        loss = uniform(1 / 3, 2 / 3)
    exponent = 1.5 #shouldnt need to change this that much
    winner, a_left, b_left = lanchester(a,b,loss,loss,exponent)
    if winner: #b wins
        return f"Side B, as the winner, has {round(b_left)} soldiers remaining, and Side A drops to {round(a_left)}"
    else: #a wins
        return f"Side A's victory leaves them with {round(a_left)} soldiers left, while Side B loses with {round(b_left)}"