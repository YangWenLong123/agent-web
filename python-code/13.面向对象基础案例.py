
"""
    采用面向对象的编程思想，完成教务管理系统的开发。教务管理系统可以管理在校学生的成绩信息，通过控制台菜单与用户交互，具体的功能如下：
        1. **添加学生成绩**：根据输入的学生姓名、语文成绩、数学成绩、英语成绩，记录在系统中。

        2. **修改学生成绩**：根据输入的学生姓名，修改对应的学生成绩。

        3. **删除学生成绩**：根据输入的学生姓名，删除对应的学生成绩。

        4. **查询指定学生成绩**：根据输入的学生姓名，查找对应的学生成绩，并输出。

        5. **展示全部学生成绩**：展示出系统中所有学生的成绩。
"""

# class Student:
#     def __init__(self, name, chinese, math, english):
#         self.name = name
#         self.chinese = chinese
#         self.math = math
#         self.english = english
#
#     def __str__(self):
#         return  f"姓名：{self.name} | 语文：{self.chinese} | 数学：{self.math} | 英语：{self.english} | 总分： {self.chinese + self.math + self.english}"
#
#     # 修改学生的成绩
#
#     def update_score(self, chinese, math, english):
#
#
#
#

















"""面向对象练习：学生成绩管理系统。

运行：python3 docs/python/examples/student_grade_system.py
约定：姓名唯一，三科成绩均为 0～100 分；数据仅保存在内存中。
"""


class Student:
    """保存一个学生的姓名和三科成绩。"""

    def __init__(self, name, chinese, math, english):
        self.name = name.strip()
        if not self.name:
            raise ValueError("姓名不能为空。")

        self.update_scores(chinese, math, english)

    @staticmethod
    def validate_score(score):
        """成绩允许整数和小数，不接受布尔值、无穷大或 NaN。"""
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError("成绩必须是数字。")
        if not 0 <= score <= 100:
            raise ValueError("成绩必须在 0～100 之间。")

    def update_scores(self, chinese, math, english):
        """全部校验通过后再更新，避免只修改了部分成绩。"""
        for score in (chinese, math, english):
            self.validate_score(score)

        self.chinese = chinese
        self.math = math
        self.english = english

    def __str__(self):
        """控制 print(student) 时显示的内容。"""
        return (
            f"姓名：{self.name} | 语文：{self.chinese:g} | "
            f"数学：{self.math:g} | 英语：{self.english:g}"
        )


class StudentManager:
    """使用字典保存学生对象，以姓名作为查找依据。"""

    def __init__(self):
        # 每个管理器拥有自己的字典，不使用共享的类属性。
        self._students = {}

    def add_student(self, name, chinese, math, english):
        name = name.strip()
        if name in self._students:
            raise ValueError("该学生已存在，请使用修改功能。")

        student = Student(name, chinese, math, english)
        self._students[name] = student

    def find_student(self, name):
        """找到时返回 Student 对象，找不到时返回 None。"""
        return self._students.get(name.strip())

    def update_student(self, name, chinese, math, english):
        student = self.find_student(name)
        if student is None:
            raise ValueError("未找到该学生。")

        student.update_scores(chinese, math, english)

    def delete_student(self, name):
        name = name.strip()
        if name not in self._students:
            raise ValueError("未找到该学生。")

        del self._students[name]

    def get_all_students(self):
        """返回所有学生，顺序为添加顺序（Python 3.7+）。"""
        return list(self._students.values())


def read_score(subject):
    """持续读取一科成绩，直到输入合法。"""
    while True:
        try:
            score = float(input(f"请输入{subject}成绩（0～100）："))
            Student.validate_score(score)
            return score
        except ValueError:
            print("输入无效，请输入 0～100 之间的数字，可以带小数。")


def read_scores():
    chinese = read_score("语文")
    math = read_score("数学")
    english = read_score("英语")
    return chinese, math, english


def show_menu():
    print("\n========== 教务管理系统 ==========")
    print("1. 添加学生成绩")
    print("2. 修改学生成绩")
    print("3. 删除学生成绩")
    print("4. 查询指定学生成绩")
    print("5. 展示全部学生成绩")
    print("0. 退出系统")


def main():
    manager = StudentManager()
    print("欢迎使用！本练习版数据仅保存在内存中，退出后清空。")

    while True:
        show_menu()
        choice = input("请选择功能（0～5）：").strip()

        if choice == "0":
            print("系统已退出。")
            break

        if choice not in ("1", "2", "3", "4", "5"):
            print("菜单选项无效，请重新选择。")
            continue

        if choice == "5":
            students = manager.get_all_students()
            if not students:
                print("暂无学生成绩。")
            else:
                print("\n全部学生成绩：")
                for student in students:
                    print(student)
            continue

        name = input("请输入学生姓名：").strip()
        if not name:
            print("姓名不能为空。")
            continue

        student = manager.find_student(name)
        if choice == "1" and student is not None:
            print("该学生已存在，请使用修改功能。")
            continue
        if choice in ("2", "3", "4") and student is None:
            print("未找到该学生。")
            continue

        try:
            if choice in ("1", "2"):
                chinese, math, english = read_scores()
                if choice == "1":
                    manager.add_student(name, chinese, math, english)
                    print("添加成功。")
                else:
                    manager.update_student(name, chinese, math, english)
                    print("修改成功。")
            elif choice == "3":
                manager.delete_student(name)
                print("删除成功。")
            elif choice == "4":
                print(student)
        except ValueError as error:
            print(error)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n系统已退出。")
