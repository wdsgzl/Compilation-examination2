from prettytable import PrettyTable
class Grammar:
    def __init__(self, rules):
        self.rules = rules
        self.non_terminals = set(rules.keys())
        self.terminals = set()  # 初始化终结符集合
        self.first = {}
        self.follow = {non_terminal: set() for non_terminal in self.non_terminals}
        for non_terminal, productions in self.rules.items():
            for production in productions:
                for symbol in production:
                    if symbol.islower():  # 假设小写字母为终结符
                        self.terminals.add(symbol)
                    # 如果有其他终结符的逻辑，请在这里添加


    def compute_first(self):
        for non_terminal in self.non_terminals:
            for production in self.rules[non_terminal]:
                first_key = ''.join(production)
                self.first[first_key] = self.first_sequence(production)


    def compute_follow(self):

        start_symbol = next(iter(self.rules))
        self.follow[start_symbol].add('$')

        while True:
            unchanged = True
            for head, productions in self.rules.items():
                for production in productions:
                    follow_changed = self.update_follow(head, production)
                    if follow_changed:
                        unchanged = False
            if unchanged:
                break

    def update_follow(self, head, production):

        follow_changed = False
        follow_temp = self.follow[head].copy()
        for i in range(len(production) - 1, -1, -1):
            symbol = production[i]
            if symbol in self.non_terminals:

                before_update = self.follow[symbol].copy()
                self.follow[symbol].update(follow_temp)
                if before_update != self.follow[symbol]:
                    follow_changed = True


                if '@' in self.first_sequence([symbol]):
                    follow_temp = follow_temp.union(self.first_sequence([symbol]) - {'@'})
                else:

                    follow_temp = self.first_sequence([symbol])
            else:

                follow_temp = {symbol}
        return follow_changed
    def first_sequence(self, sequence):
        if not sequence:
            return {"@"}
        first = set()
        for symbol in sequence:
            if symbol in self.non_terminals:
                for prod in self.rules[symbol]:
                    first_of_symbol = self.first_sequence(prod)
                    first.update(first_of_symbol - {"@"})
                    if "@" not in first_of_symbol:
                        break
                else:
                    continue
                break
            else:
                first.add(symbol)
                break
        return first

    def display_sets(self):
        print("First集:")
        for production, first_set in self.first.items():
            print(f"First({production}) = {first_set}")
        print("\nFollow集:")
        for non_terminal, follow_set in self.follow.items():
            print(f"Follow({non_terminal}) = {follow_set}")

    def construct_ll1_table(self):
        self.table = {}
        for non_terminal in self.non_terminals:
            self.table[non_terminal] = {}
            for production in self.rules[non_terminal]:
                first_of_production = self.first_sequence(production)
                for terminal in first_of_production - {'@'}:
                    self.table[non_terminal][terminal] = production
                if '@' in first_of_production:
                    for follow_symbol in self.follow[non_terminal]:
                        self.table[non_terminal][follow_symbol] = production
                    if '$' in self.follow[non_terminal]:
                        self.table[non_terminal]['$'] = production

    def display_ll1_table(self):
        # 获取所有的终结符，包括'$'
        terminals = set(
            term for prod_list in self.rules.values() for prod in prod_list for term in prod if term in self.terminals)
        terminals.add('$')

        # 创建一个表格，并为每个终结符添加一个列标题
        table = PrettyTable()
        table.field_names = ["终结|非终结"] + sorted(terminals)

        # 填充表格的每一行
        for non_terminal in sorted(self.non_terminals):
            row = [non_terminal]
            for terminal in sorted(terminals):
                production = self.table.get(non_terminal, {}).get(terminal, "")
                if production:
                    row.append(f"{non_terminal} -> {' '.join(production)}")
                else:
                    row.append(" ")
            table.add_row(row)

        print(table)

    def parse_input(self, input_string):
        input_tokens = list(input_string) + ['$']  # 假设'$'表示输入的结束
        stack = ['$']  # 初始化栈，'$'表示栈底
        start_symbol = next(iter(self.rules))  # 获取文法的开始符号
        stack.append(start_symbol)  # 将开始符号压入栈中

        print("分析过程")
        print(f"{'分析栈':<20}{'预留输入串':<20}{'产生式':<20}")
        while len(stack) > 0:
            top = stack[-1]
            current_input = input_tokens[0]
            if top == current_input == '$':  # 成功匹配到输入结束
                print(f"{' '.join(stack):<20}{' '.join(input_tokens):<20}{'Accept':<20}")
                return "该串是文法的句子"
            elif top in self.terminals or top == '$':  # 栈顶是终结符或栈底符号
                if top == current_input:  # 匹配成功
                    stack.pop()  # 弹出栈顶
                    input_tokens.pop(0)  # 移动到输入的下一个字符
                    print(f"{' '.join(stack):<20}{' '.join(input_tokens):<20}{'Match':<20}")
                else:
                    print(f"{' '.join(stack):<20}{' '.join(input_tokens):<20}{'Error':<20}")
                    return "该串不是文法的句子"
            else:  # 栈顶是非终结符
                rule = self.table.get(top, {}).get(current_input, None)
                if rule is not None:
                    print(f"{' '.join(stack):<20}{' '.join(input_tokens):<20}{top + ' -> ' + ' '.join(rule):<20}")
                    stack.pop()  # 弹出栈顶非终结符
                    if rule != ['@']:  # '@'表示空串
                        for symbol in reversed(rule):  # 倒序压入栈中，因为栈是LIFO
                            stack.append(symbol)
                else:
                    print(f"{' '.join(stack):<20}{' '.join(input_tokens):<20}{'Error':<20}")
                    return "该串不是文法的句子"
        return "该串不是文法的句子"

def parse_grammar_from_file(file_path):
    rules = {}
    with open(file_path, 'r') as file:
        for line in file:
            head, productions = line.split("::=")
            rules[head.strip()] = [production.strip().split() for production in productions.split("|")]
    return rules


grammar_rules = parse_grammar_from_file('data.txt')
grammar = Grammar(grammar_rules)
grammar.compute_first()
grammar.compute_follow()
grammar.display_sets()
grammar.construct_ll1_table()
grammar.display_ll1_table()

input_string = "a"  # 假设这是用户输入的字符串
result = grammar.parse_input(input_string)
print(result)