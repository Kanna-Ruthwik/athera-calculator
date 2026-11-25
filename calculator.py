import ast
import operator
import gi

gi.require_version("Gtk","4.0")
from gi.repository import Gtk, Gdk
OPS = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.truediv,
}

def calculate(expression):
	def evaluate(node):
		if isinstance(node,ast.Expression):
			return evaluate(node.body)
		if isinstance(node,ast.Constant) and type(node.value) in (int,float):
			return node.value
		if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
			value = evaluate(node.operand)
			return value if isinstance(node.op,ast.UAdd) else -value
		if isinstance(node,ast.BinOp) and type(node.op) in OPS:
			return OPS[type(node.op)](
				evaluate(node.left),evaluate(node.right)
			)
		raise ValueError("Invalid Expression")
	tree = ast.parse(expression,mode="eval")
	return evaluate(tree)

class AtheraCalculator(Gtk.Application):
	def __init__(self):
		super().__init__(application_id="com.athera.calculator")
		self.expression = ""
	def do_activate(self):
		self.window = Gtk.ApplicationWindow(application=self)
		self.window.set_title("Athera Calculator")
		self.window.set_default_size(340,490)
		self.window.set_resizable(False)
		
		root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=12)
		root.set_margin_top(20)
		root.set_margin_bottom(20)
		root.set_margin_start(20)
		root.set_margin_end(20)
		self.window.set_child(root)
		
		heading = Gtk.Label(label="ATHERA / CALCULATOR")
		heading.add_css_class("heading")
		root.append(heading)
		
		self.display = Gtk.Label(label="0")
		self.display.set_xalign(1)
		self.display.set_yalign(1)
		self.display.set_wrap(True)
		self.display.set_size_request(-1,100)
		self.display.add_css_class("display")
		root.append(self.display)
		
		grid = Gtk.Grid()
		grid.set_row_spacing(8)
		grid.set_column_spacing(8)
		grid.set_column_homogeneous(True)
		grid.set_row_homogeneous(True)
		root.append(grid)

		keys = [
			"AC","±","%","÷",
			"7","8","9","×",
			"4","5","6","-",
			"1","2","3","+",
			"⌫","0",".","="
			]
		for index, key in enumerate(keys):
			button = Gtk.Button(label=key)
			button.add_css_class("calc-button")
			if key in ("÷","×","-","+","="):
				button.add_css_class("operator")
			button.connect("clicked",self.on_button,key)
			grid.attach(button,index%4,index//4,1,1)
		self.apply_css()
		controller = Gtk.EventControllerKey()
		controller.connect("key-pressed",self.on_key)
		self.window.add_controller(controller)
		self.window.present()

	def update(self):
		self.display.set_text(self.expression or "0")

	def on_button(self,button,key):
		if key == "AC":
			self.expression = ""
		elif key == "⌫":
			self.expression = self.expression[:-1]
		elif key == "=":
			try:
				result = calculate(self.expression)
				self.expression = format(result,".12g")
			except Exception:
				self.expression = "Error"
		elif key =="±":
			if self.expression and self.expression != "Error":
				try:
					self.expression = format(
						-calculate(self.expression),".12g"
					)
				except Exception:
					pass
		elif key =="%":
			try:
				self.expression = format(calculate(self.expression)/100,".12g")
			except Exception:
				self.expression = "Error"
		else:
			if self.expression == "Error":
				self.expression = ""
			if key =="0" and (not self.expression or self.expression =="0"):
				return
			if key.isdigit() and self.expression =="0":
				self.expression = key
			else:
				self.expression += {"÷":"/","×":"*","-":"-"}.get(key,key)
		self.update()
	
	def on_key(self,controller,keyval,keycode,state):
		key = Gdk.keyval_name(keyval)
		if key in ("Return","KP_Enter"):
			self.on_button(None,"=")
		elif key == "BackSpace":
			self.on_button(None,"⌫")
		elif key == "Escape":
			self.on_button(None,"AC")
		elif key in ("plus","minus","asterisk","slash"):
			self.expression  += {"plus":"+","minus":"-","asterisk":"*","slash":"/"}[key]
			self.update()
		elif key and (key.isdigit() or key == "period"):
			self.expression += "." if key == "period" else key
			self.update()
		return True

	def apply_css(self):
		css = b"""
		window = {
			background: #10141f;
			color:#f46fb;
		}
		.heading{
			color:#8fa9d8;
			font-size:13px;
			font-weight:bold;
		}
		.display{
			color:#00000;
			font-size:38px;
			font-weight:bold;
			padding:18px 5px;
		}
		.calc-button{
			min-height:57px;
			font-size:20px;
			font-weight:bold;
			background:#20283a;
			color:#ffffff;
		}
		.operator{
			background:#315eaa;
			color:white;
		}
		button:hover{
			background:#405477;
		}
		"""
		provider = Gtk.CssProvider()
		provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_display(
			Gdk.Display.get_default(),
			provider,
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
app = AtheraCalculator()
app.run()
