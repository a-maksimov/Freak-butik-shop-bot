"""
This function checks if phone number is correct
"""


def correct_number(string):
    correct = True
    number_list = string.split('-')
    if len(number_list) == 3:
        if len(number_list[0]) == len(number_list[1]) == 3 and len(number_list[2]) == 4:
            for i in range(len(number_list)):
                if number_list[i].isdigit():
                    new_correct = True
                else:
                    new_correct = False
                    break
            correct = correct and new_correct
        else:
            correct = False
    elif len(number_list) == 4:
        if (len(number_list[0]) == 1 and number_list[0].isdigit() and int(number_list[0]) == 7) \
                and len(number_list[1]) == len(number_list[2]) == 3 and len(number_list[3]) == 4:
            for i in range(1, len(number_list)):
                if number_list[i].isdigit():
                    new_correct = True
                else:
                    new_correct = False
                    break
            correct = correct and new_correct
        else:
            correct = False
    else:
        correct = False

    if correct:
        return True
    else:
        return False

# Верное решение #197295645
# Python 3
# n = input().split("-")
# c = [len(i) for i in n]
# if c == [3, 3, 4] and ''.join(n).isdigit():
#     print("YES")
# elif c == [1, 3, 3, 4] and ''.join(n).isdigit() and n[0] == '7':
#     print("YES")
# else:
#     print("NO")
