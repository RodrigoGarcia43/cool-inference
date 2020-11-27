from cool_inference.inference.tybags import TyBags
from cool_inference.utils.lca import lowest_common_ancestor
import cool_inference.utils.visitor as visitor
from cool_inference.semantics.semantics import (
    IntType,
    BoolType,
    StringType,
    AutoType,
)
from cool_inference.ast import (
    Program,
    CoolClass,
    FuncDecl,
    AttrDecl,
    Assign,
    Not,
    IsVoid,
    Tilde,
    Dispatch,
    StaticDispatch,
    IfThenElse,
    WhileLoop,
    LetIn,
    Case,
    NewType,
    ParenthExp,
    IdExp,
    Block,
    IntExp,
    StringExp,
    BoolExp,
    Plus,
    Minus,
    Mult,
    Div,
    Le,
    Leq,
    Eq,
)


class BagsCollector:
    def __init__(self, context, errors=[]):  # noqa: F811
        self.context = context
        self.errors = errors

    @visitor.on("node")
    def visit(self, node, bags):  # noqa: F811
        pass

    @visitor.when(Program)
    def visit(self, node, tybags=None):  # noqa: F811
        tybags = TyBags()

        for cool_class in node.cool_class_list:
            self.visit(cool_class, tybags)
        return tybags

    @visitor.when(CoolClass)
    def visit(self, node, tybags):  # noqa: F811
        tybags = tybags.create_child(node)

        self.current_type = self.context.get_type(node.id)

        tybags.define_variable("self", [self.current_type.name])

        for method in self.current_type.methods:
            if method.return_type == AutoType():
                types = list(self.context.types.keys())
            else:
                types = [method.return_type.name]

            tybags.define_variable(method.name, types)

        for attr in self.current_type.attributes:
            if attr.type == AutoType():
                types = list(self.context.types.keys())
            else:
                types = [attr.type.name]
            tybags.define_variable(attr.name, types)

        for feat in node.feature_list:
            self.visit(feat, tybags)
        return tybags

    @visitor.when(AttrDecl)
    def visit(self, node, tybags):  # noqa: F811
        return

    @visitor.when(FuncDecl)
    def visit(self, node, tybags):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_tybags = tybags.create_child(node)
        self.current_method.tybags = method_tybags

        for pname, ptype in zip(
            self.current_method.param_names, self.current_method.param_types
        ):
            if ptype == AutoType():
                method_tybags.define_variable(pname, list(self.context.types.keys()))
            else:
                method_tybags.define_variable(pname, [ptype.name])

        self.visit(node.body, method_tybags)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, tybags):  # noqa: F811
        return

    @visitor.when(Dispatch)
    def visit(self, node, tybags):  # noqa: F811
        return

    @visitor.when(StaticDispatch)
    def visit(self, node, tybags):  # noqa: F811
        return

    @visitor.when(LetIn)
    def visit(self, node, tybags):  # noqa: F811
        let_tybags = tybags.create_child(node)
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, _ in decl_list:
            typex = self.context.get_type(_type)

            if typex == AutoType():
                let_tybags.define_variable(idx, list(self.context.types.keys()))
            else:
                let_tybags.define_variable(idx, [typex.name])

        self.visit(exp, let_tybags)

    # TODO
    @visitor.when(Case)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.create_child(case_exp)

            typex = self.context.get_type(typex)

            if typex == AutoType():
                new_tybags.define_variable(idx, list(self.context.types.keys()))
            else:
                new_tybags.define_variable(idx, [typex.name])

            self.visit(case_exp, new_tybags)

    @visitor.when(Block)
    def visit(self, node, tybags):  # noqa: F811
        for exp in node.expr_list:
            self.visit(exp, tybags)

    @visitor.when(Not)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    # TODO
    @visitor.when(Tilde)
    def visit(self, node, tybags):  # noqa: F811
        return

    @visitor.when(IsVoid)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    @visitor.when(ParenthExp)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.exp, tybags)

    def arith(self, node, tybags):  # noqa: F811

        self.visit(node.left, tybags)
        self.visit(node.right, tybags)

    @visitor.when(Plus)
    def visit(self, node, tybags):  # noqa: F811
        self.arith(node, tybags)

    @visitor.when(Minus)
    def visit(self, node, tybags):  # noqa: F811
        self.arith(node, tybags)

    @visitor.when(Div)
    def visit(self, node, tybags):  # noqa: F811
        self.arith(node, tybags)

    @visitor.when(Mult)
    def visit(self, node, tybags):  # noqa: F811
        self.arith(node, tybags)

    def comp(self, node, tybags):  # noqa: F811
        self.visit(node.left, tybags)
        self.visit(node.right, tybags)

    @visitor.when(Leq)
    def visit(self, node, tybags):  # noqa: F811
        self.comp(node, tybags)

    @visitor.when(Eq)
    def visit(self, node, tybags):  # noqa: F811
        self.comp(node, tybags)

    @visitor.when(Le)
    def visit(self, node, tybags):  # noqa: F811
        self.comp(node, tybags)

    @visitor.when(WhileLoop)
    def visit(self, node, tybags):  # noqa: F811
        pass
        self.visit(node.left, tybags)
        self.visit(node.right, tybags)

    @visitor.when(IfThenElse)
    def visit(self, node, tybags):  # noqa: F811
        self.visit(node.first, tybags)
        self.visit(node.second, tybags)
        self.visit(node.third, tybags)

    @visitor.when(StringExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(BoolExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IntExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(IdExp)
    def visit(self, node, tybags):  # noqa: F811
        pass

    @visitor.when(NewType)
    def visit(self, node, tybags):  # noqa: F811
        pass


class BagsReducer:
    def __init__(self, tybags, context, errors=[]):
        self.current_type = None
        self.current_method = None
        self.context = context
        self.errors = errors
        self.tybags = tybags

    @visitor.on("node")
    def visit(self, node, tybags, restriction):
        pass

    @visitor.when(Program)
    def visit(self, node, tybags=None, restriction=None):  # noqa: F811
        tybags = TyBags()
        print(tybags.compare(self.tybags))

        while not self.tybags.compare(tybags):
            tybags.clone(self.tybags)

            for cool_class in node.cool_class_list:
                self.visit(cool_class, self.tybags, [])
            self.tybags.clean()

        return self.tybags

    @visitor.when(CoolClass)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.current_type = self.context.get_type(node.id)
        tybags = tybags.children[node]

        for feat in node.feature_list:
            self.visit(feat, tybags, [])
        self.current_type = None

    @visitor.when(AttrDecl)
    def visit(self, node, tybags, restriction):  # noqa: F811
        if node.body is not None:
            tybags.reduce_bag(node, self.visit(node.body, tybags, []))

    @visitor.when(FuncDecl)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.current_method = self.current_type.get_method(node.id)
        method_tybags = tybags.children[node]

        return_types = self.visit(node.body, method_tybags, [])

        method_tybags.reduce_bag(node, return_types)

        self.current_method = None

    @visitor.when(Assign)
    def visit(self, node, tybags, restriction):  # noqa: F811
        types = self.visit(node.value, tybags, [])

        tybags.reduce_bag(node, types)
        return tybags.find_variable(node.id)

    # TODO fix dispatch. Find an elegant way to do it.
    @visitor.when(Dispatch)
    def visit(self, node, tybags, restriction):  # noqa: F811
        exp_types = self.visit(node.exp, tybags, [])
        if len(exp_types) > 1:
            types_whith_method = []
            return_types = []
            for key, value in self.context.types.items():
                for method in value.methods:
                    if (
                        key in exp_types
                        and method.name == node.id
                        and len(method.param_names) == len(node.exp_list)
                    ):
                        types_whith_method.append(key)
                        return_types.append(method.return_type.name)
                        break

            if len(types_whith_method) == 0:
                error = f"""
                There is not possible type of expression that
                have {node.id} method with {len(node.exp_list)} params
                """
                if error not in self.errors:
                    self.errors.append(error)
                return set([self.context.types["ERROR"]])

            tybags.reduce_bag(node.exp, types_whith_method)
            return set(return_types)

        elif len(exp_types) == 1:
            exp_type = self.context.types[list(exp_types)[0]]
            method = exp_type.get_method(node.id)

            function_ty = method.tybags

            for arg, param in zip(node.exp_list, method.param_names):
                arg_types = self.visit(arg, tybags, function_ty.vars[param])
                function_ty.reduce_bag(None, arg_types, name=param)

            return function_ty.find_variable(node.id)

    # TODO
    @visitor.when(StaticDispatch)
    def visit(self, node, tybags, restriction):  # noqa: F811
        pass

    @visitor.when(LetIn)
    def visit(self, node, tybags, restriction):  # noqa: F811
        let_tybags = tybags.children[node]
        decl_list, exp = node.decl_list, node.exp

        for idx, _type, expx in decl_list:
            # typex = self.context.get_type(_type)

            if expx is not None:
                tybags.reduce_bag(node, self.visit(expx, tybags, []))

        let_types = self.visit(exp, let_tybags, [])

        return let_types

    # TODO
    @visitor.when(Case)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])
        return_types = []
        ances_type = None

        for idx, typex, case_exp in node.case_list:

            new_tybags = tybags.children[case_exp]

            typex = self.context.get_type(typex)

            static_types = self.visit(case_exp, new_tybags, [])

            if len(static_types) == 0:
                ances_type = lowest_common_ancestor(
                    ances_type, self.context.get_type[static_types[0]], self.context
                )

            else:
                return_types = set.union(set(return_types), set(static_types))

        return set.union(set(return_types), set([ances_type.name]))

    @visitor.when(Block)
    def visit(self, node, tybags, restriction):  # noqa: F811
        li = []
        for exp in node.expr_list[0 : len(node.expr_list) - 1]:
            exp_types = self.visit(exp, tybags, li)

        last = node.expr_list[len(node.expr_list) - 1]
        exp_types = self.visit(last, tybags, restriction)
        if len(restriction) > 0:
            tybags.reduce_bag(last, restriction)

        return exp_types

    @visitor.when(Not)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])

        return set([BoolType().name])

    # TODO
    @visitor.when(Tilde)
    def visit(self, node, tybags, restriction):  # noqa: F811
        pass

    @visitor.when(IsVoid)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.exp, tybags, [])
        return set([BoolType().name])

    @visitor.when(ParenthExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        self.visit(node.exp, tybags, [])

    def arith(self, node, tybags):
        _ = self.visit(node.left, tybags, [IntType().name])
        _ = self.visit(node.right, tybags, [IntType().name])
        tybags.reduce_bag(node.left, [IntType().name])
        tybags.reduce_bag(node.right, [IntType().name])
        return set([IntType().name])

    @visitor.when(Plus)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    @visitor.when(Minus)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    @visitor.when(Div)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    @visitor.when(Mult)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.arith(node, tybags)

    def comp(self, node, tybags):
        _ = self.visit(node.left, tybags, [])
        _ = self.visit(node.right, tybags, [])
        return set([BoolType().name])

    @visitor.when(Leq)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.comp(node, tybags)

    @visitor.when(Eq)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.comp(node, tybags)

    @visitor.when(Le)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return self.comp(node, tybags)

    @visitor.when(WhileLoop)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.left, tybags, [BoolType().name])
        _ = self.visit(node.right, tybags, [])

        return set([self.context.get_type("Object").name])

    @visitor.when(IfThenElse)
    def visit(self, node, tybags, restriction):  # noqa: F811
        _ = self.visit(node.first, tybags, [BoolType().name])
        then_types = self.visit(node.second, tybags, [])
        else_types = self.visit(node.third, tybags, [])

        inters = then_types & else_types

        if len(inters) > 0:
            return inters

        return set.union(then_types, else_types)

    @visitor.when(StringExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([StringType().name])

    @visitor.when(BoolExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([BoolType().name])

    @visitor.when(IntExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([IntType().name])

    @visitor.when(IdExp)
    def visit(self, node, tybags, restriction):  # noqa: F811
        if len(restriction) > 0:
            tybags.reduce_bag(node, restriction)

        return tybags.find_variable(node.id)

    @visitor.when(NewType)
    def visit(self, node, tybags, restriction):  # noqa: F811
        return set([node.type])
