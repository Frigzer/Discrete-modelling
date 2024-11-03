import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def handle_border(state, i, boundary):
    if boundary == "periodic":
        if i > 0:
            left = state[i - 1]
        else:
            left = state[-1]

        if i < len(state) - 1:
            right = state[i + 1]
        else:
            right = state[0]
    else:
        if i > 0:
            left = state[i - 1]
        else:
            left = 0

        if i < len(state) - 1:
            right = state[i + 1]
        else:
            right = 0

    return left, right


def rule_to_bin(rule_number):
    return np.array([int(x) for x in f"{rule_number:08b}"])


def compute_new_state(cell, left, right, rule):
    index = 7 - (left * 4 + cell * 2 + right)
    return rule[index]


def automaton(initial_state, rules, iterations, boundary="periodic"):
    if boundary == "periodic":
        print("Ustawiono warunek brzegowy 'periodic'.")
    else:
        print("Ustawiono warunek brzegowy 'absorbing'.")
    states = [initial_state.copy()]
    rule_sets = [rule_to_bin(r) for r in rules]

    for j in range(iterations):
        new_state = initial_state.copy()
        for i in range(len(initial_state)):
            left, right = handle_border(initial_state, i, boundary)

            rule = rule_sets[j % len(rule_sets)]
            new_state[i] = compute_new_state(initial_state[i], left, right, rule)

        initial_state = new_state
        states.append(new_state.copy())

    return states


def save_to_csv(states, filename="automaton_output.csv"):
    df = pd.DataFrame(states)
    df.to_csv(filename, index=False, header=False)


def generate_state():
    initial_state_string = input("Podaj stan poczatkowy: ")
    if initial_state_string == "random":
        size = get_input("Podaj rozmiar stanu początkowego: ", 3)
        initial_state = np.random.choice([0, 1], size=size)
    else:
        try:
            initial_state = list(map(int, initial_state_string.split(", ")))
            if len(initial_state) < 3:
                print("Nieprawidłowy stan, ustawiono domyślny.")
                return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
            for i in range(0, len(initial_state)):
                if initial_state[i] != 0 and initial_state[i] != 1:
                    initial_state[i] = 0

            return np.array(initial_state)

        except ValueError:
            print("Nieprawidłowy stan, ustawiono domyślny.")
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1]
    return initial_state


def get_input(prompt, min_value=1):
    while True:
        try:
            value = int(input(prompt))
            if value >= min_value:
                return value
            else:
                print(f"Wartość musi być większa lub równa {min_value}.")
        except ValueError:
            print("Proszę wprowadzić liczbę całkowitą.")


def visualize_grid(matrix : np.ndarray):
    custom_cmap = ListedColormap(["#FFFFFF", "#ff6600"]) # 0 i 1

    plt.imshow(matrix, cmap=custom_cmap, interpolation='nearest')

    ax = plt.gca()
    ax.set_xticks(np.arange(-0.5, matrix.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, matrix.shape[0], 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", size=0)

    plt.xticks([])
    plt.yticks([])

    plt.show()


def main():
    album_number = "416965"
    rules = [int(album_number[i:i + 2]) for i in range(0, len(album_number), 2)] + [190]
    #rules = [106]
    #rules = [112]
    initial_state = generate_state()

    iterations = get_input("Podaj liczbę iteracji: ")

    boundary_type = input("Wybierz warunek brzegowy (periodic/absorbing): ").strip().lower()

    states = automaton(initial_state, rules, iterations, boundary_type)

    save_to_csv(states)

    print(f"Wynik zapisano w pliku automaton_output.csv")

    visualize_grid(np.array(states))


if __name__ == "__main__":
    main()
