import { r as __toESM, t as require_react } from "./react-DV3nHG90.js";
//#region node_modules/react-flow-renderer/node_modules/zustand/esm/index.js
var import_react = /* @__PURE__ */ __toESM(require_react());
function createStore$1(createState) {
	let state;
	const listeners = /* @__PURE__ */ new Set();
	const setState = (partial, replace) => {
		const nextState = typeof partial === "function" ? partial(state) : partial;
		if (nextState !== state) {
			const previousState = state;
			state = replace ? nextState : Object.assign({}, state, nextState);
			listeners.forEach((listener) => listener(state, previousState));
		}
	};
	const getState = () => state;
	const subscribeWithSelector = (listener, selector = getState, equalityFn = Object.is) => {
		console.warn("[DEPRECATED] Please use `subscribeWithSelector` middleware");
		let currentSlice = selector(state);
		function listenerToAdd() {
			const nextSlice = selector(state);
			if (!equalityFn(currentSlice, nextSlice)) {
				const previousSlice = currentSlice;
				listener(currentSlice = nextSlice, previousSlice);
			}
		}
		listeners.add(listenerToAdd);
		return () => listeners.delete(listenerToAdd);
	};
	const subscribe = (listener, selector, equalityFn) => {
		if (selector || equalityFn) return subscribeWithSelector(listener, selector, equalityFn);
		listeners.add(listener);
		return () => listeners.delete(listener);
	};
	const destroy = () => listeners.clear();
	const api = {
		setState,
		getState,
		subscribe,
		destroy
	};
	state = createState(setState, getState, api);
	return api;
}
var useIsomorphicLayoutEffect = typeof window === "undefined" || !window.navigator || /ServerSideRendering|^Deno\//.test(window.navigator.userAgent) ? import_react.useEffect : import_react.useLayoutEffect;
function create$1(createState) {
	const api = typeof createState === "function" ? createStore$1(createState) : createState;
	const useStore = (selector = api.getState, equalityFn = Object.is) => {
		const [, forceUpdate] = (0, import_react.useReducer)((c) => c + 1, 0);
		const state = api.getState();
		const stateRef = (0, import_react.useRef)(state);
		const selectorRef = (0, import_react.useRef)(selector);
		const equalityFnRef = (0, import_react.useRef)(equalityFn);
		const erroredRef = (0, import_react.useRef)(false);
		const currentSliceRef = (0, import_react.useRef)();
		if (currentSliceRef.current === void 0) currentSliceRef.current = selector(state);
		let newStateSlice;
		let hasNewStateSlice = false;
		if (stateRef.current !== state || selectorRef.current !== selector || equalityFnRef.current !== equalityFn || erroredRef.current) {
			newStateSlice = selector(state);
			hasNewStateSlice = !equalityFn(currentSliceRef.current, newStateSlice);
		}
		useIsomorphicLayoutEffect(() => {
			if (hasNewStateSlice) currentSliceRef.current = newStateSlice;
			stateRef.current = state;
			selectorRef.current = selector;
			equalityFnRef.current = equalityFn;
			erroredRef.current = false;
		});
		const stateBeforeSubscriptionRef = (0, import_react.useRef)(state);
		useIsomorphicLayoutEffect(() => {
			const listener = () => {
				try {
					const nextState = api.getState();
					const nextStateSlice = selectorRef.current(nextState);
					if (!equalityFnRef.current(currentSliceRef.current, nextStateSlice)) {
						stateRef.current = nextState;
						currentSliceRef.current = nextStateSlice;
						forceUpdate();
					}
				} catch (error) {
					erroredRef.current = true;
					forceUpdate();
				}
			};
			const unsubscribe = api.subscribe(listener);
			if (api.getState() !== stateBeforeSubscriptionRef.current) listener();
			return unsubscribe;
		}, []);
		const sliceToReturn = hasNewStateSlice ? newStateSlice : currentSliceRef.current;
		(0, import_react.useDebugValue)(sliceToReturn);
		return sliceToReturn;
	};
	Object.assign(useStore, api);
	useStore[Symbol.iterator] = function() {
		console.warn("[useStore, api] = create() is deprecated and will be removed in v4");
		const items = [useStore, api];
		return { next() {
			const done = items.length <= 0;
			return {
				value: items.shift(),
				done
			};
		} };
	};
	return useStore;
}
//#endregion
//#region node_modules/react-flow-renderer/node_modules/zustand/esm/context.js
function createContext$2() {
	const ZustandContext = (0, import_react.createContext)(void 0);
	const Provider = ({ initialStore, createStore, children }) => {
		const storeRef = (0, import_react.useRef)();
		if (!storeRef.current) {
			if (initialStore) {
				console.warn("Provider initialStore is deprecated and will be removed in the next version.");
				if (!createStore) createStore = () => initialStore;
			}
			storeRef.current = createStore();
		}
		return (0, import_react.createElement)(ZustandContext.Provider, { value: storeRef.current }, children);
	};
	const useStore = (selector, equalityFn = Object.is) => {
		const useProviderStore = (0, import_react.useContext)(ZustandContext);
		if (!useProviderStore) throw new Error("Seems like you have not used zustand provider as an ancestor.");
		return useProviderStore(selector, equalityFn);
	};
	const useStoreApi = () => {
		const useProviderStore = (0, import_react.useContext)(ZustandContext);
		if (!useProviderStore) throw new Error("Seems like you have not used zustand provider as an ancestor.");
		return (0, import_react.useMemo)(() => ({
			getState: useProviderStore.getState,
			setState: useProviderStore.setState,
			subscribe: useProviderStore.subscribe,
			destroy: useProviderStore.destroy
		}), [useProviderStore]);
	};
	return {
		Provider,
		useStore,
		useStoreApi
	};
}
//#endregion
//#region node_modules/d3-dispatch/src/dispatch.js
var noop = { value: () => {} };
function dispatch() {
	for (var i = 0, n = arguments.length, _ = {}, t; i < n; ++i) {
		if (!(t = arguments[i] + "") || t in _ || /[\s.]/.test(t)) throw new Error("illegal type: " + t);
		_[t] = [];
	}
	return new Dispatch(_);
}
function Dispatch(_) {
	this._ = _;
}
function parseTypenames$1(typenames, types) {
	return typenames.trim().split(/^|\s+/).map(function(t) {
		var name = "", i = t.indexOf(".");
		if (i >= 0) name = t.slice(i + 1), t = t.slice(0, i);
		if (t && !types.hasOwnProperty(t)) throw new Error("unknown type: " + t);
		return {
			type: t,
			name
		};
	});
}
Dispatch.prototype = dispatch.prototype = {
	constructor: Dispatch,
	on: function(typename, callback) {
		var _ = this._, T = parseTypenames$1(typename + "", _), t, i = -1, n = T.length;
		if (arguments.length < 2) {
			while (++i < n) if ((t = (typename = T[i]).type) && (t = get$1(_[t], typename.name))) return t;
			return;
		}
		if (callback != null && typeof callback !== "function") throw new Error("invalid callback: " + callback);
		while (++i < n) if (t = (typename = T[i]).type) _[t] = set$1(_[t], typename.name, callback);
		else if (callback == null) for (t in _) _[t] = set$1(_[t], typename.name, null);
		return this;
	},
	copy: function() {
		var copy = {}, _ = this._;
		for (var t in _) copy[t] = _[t].slice();
		return new Dispatch(copy);
	},
	call: function(type, that) {
		if ((n = arguments.length - 2) > 0) for (var args = new Array(n), i = 0, n, t; i < n; ++i) args[i] = arguments[i + 2];
		if (!this._.hasOwnProperty(type)) throw new Error("unknown type: " + type);
		for (t = this._[type], i = 0, n = t.length; i < n; ++i) t[i].value.apply(that, args);
	},
	apply: function(type, that, args) {
		if (!this._.hasOwnProperty(type)) throw new Error("unknown type: " + type);
		for (var t = this._[type], i = 0, n = t.length; i < n; ++i) t[i].value.apply(that, args);
	}
};
function get$1(type, name) {
	for (var i = 0, n = type.length, c; i < n; ++i) if ((c = type[i]).name === name) return c.value;
}
function set$1(type, name, callback) {
	for (var i = 0, n = type.length; i < n; ++i) if (type[i].name === name) {
		type[i] = noop, type = type.slice(0, i).concat(type.slice(i + 1));
		break;
	}
	if (callback != null) type.push({
		name,
		value: callback
	});
	return type;
}
var namespaces_default = {
	svg: "http://www.w3.org/2000/svg",
	xhtml: "http://www.w3.org/1999/xhtml",
	xlink: "http://www.w3.org/1999/xlink",
	xml: "http://www.w3.org/XML/1998/namespace",
	xmlns: "http://www.w3.org/2000/xmlns/"
};
//#endregion
//#region node_modules/d3-selection/src/namespace.js
function namespace_default(name) {
	var prefix = name += "", i = prefix.indexOf(":");
	if (i >= 0 && (prefix = name.slice(0, i)) !== "xmlns") name = name.slice(i + 1);
	return namespaces_default.hasOwnProperty(prefix) ? {
		space: namespaces_default[prefix],
		local: name
	} : name;
}
//#endregion
//#region node_modules/d3-selection/src/creator.js
function creatorInherit(name) {
	return function() {
		var document = this.ownerDocument, uri = this.namespaceURI;
		return uri === "http://www.w3.org/1999/xhtml" && document.documentElement.namespaceURI === "http://www.w3.org/1999/xhtml" ? document.createElement(name) : document.createElementNS(uri, name);
	};
}
function creatorFixed(fullname) {
	return function() {
		return this.ownerDocument.createElementNS(fullname.space, fullname.local);
	};
}
function creator_default(name) {
	var fullname = namespace_default(name);
	return (fullname.local ? creatorFixed : creatorInherit)(fullname);
}
//#endregion
//#region node_modules/d3-selection/src/selector.js
function none() {}
function selector_default(selector) {
	return selector == null ? none : function() {
		return this.querySelector(selector);
	};
}
//#endregion
//#region node_modules/d3-selection/src/selection/select.js
function select_default$2(select) {
	if (typeof select !== "function") select = selector_default(select);
	for (var groups = this._groups, m = groups.length, subgroups = new Array(m), j = 0; j < m; ++j) for (var group = groups[j], n = group.length, subgroup = subgroups[j] = new Array(n), node, subnode, i = 0; i < n; ++i) if ((node = group[i]) && (subnode = select.call(node, node.__data__, i, group))) {
		if ("__data__" in node) subnode.__data__ = node.__data__;
		subgroup[i] = subnode;
	}
	return new Selection$1(subgroups, this._parents);
}
//#endregion
//#region node_modules/d3-selection/src/array.js
function array(x) {
	return x == null ? [] : Array.isArray(x) ? x : Array.from(x);
}
//#endregion
//#region node_modules/d3-selection/src/selectorAll.js
function empty() {
	return [];
}
function selectorAll_default(selector) {
	return selector == null ? empty : function() {
		return this.querySelectorAll(selector);
	};
}
//#endregion
//#region node_modules/d3-selection/src/selection/selectAll.js
function arrayAll(select) {
	return function() {
		return array(select.apply(this, arguments));
	};
}
function selectAll_default$1(select) {
	if (typeof select === "function") select = arrayAll(select);
	else select = selectorAll_default(select);
	for (var groups = this._groups, m = groups.length, subgroups = [], parents = [], j = 0; j < m; ++j) for (var group = groups[j], n = group.length, node, i = 0; i < n; ++i) if (node = group[i]) {
		subgroups.push(select.call(node, node.__data__, i, group));
		parents.push(node);
	}
	return new Selection$1(subgroups, parents);
}
//#endregion
//#region node_modules/d3-selection/src/matcher.js
function matcher_default(selector) {
	return function() {
		return this.matches(selector);
	};
}
function childMatcher(selector) {
	return function(node) {
		return node.matches(selector);
	};
}
//#endregion
//#region node_modules/d3-selection/src/selection/selectChild.js
var find = Array.prototype.find;
function childFind(match) {
	return function() {
		return find.call(this.children, match);
	};
}
function childFirst() {
	return this.firstElementChild;
}
function selectChild_default(match) {
	return this.select(match == null ? childFirst : childFind(typeof match === "function" ? match : childMatcher(match)));
}
//#endregion
//#region node_modules/d3-selection/src/selection/selectChildren.js
var filter = Array.prototype.filter;
function children() {
	return Array.from(this.children);
}
function childrenFilter(match) {
	return function() {
		return filter.call(this.children, match);
	};
}
function selectChildren_default(match) {
	return this.selectAll(match == null ? children : childrenFilter(typeof match === "function" ? match : childMatcher(match)));
}
//#endregion
//#region node_modules/d3-selection/src/selection/filter.js
function filter_default$1(match) {
	if (typeof match !== "function") match = matcher_default(match);
	for (var groups = this._groups, m = groups.length, subgroups = new Array(m), j = 0; j < m; ++j) for (var group = groups[j], n = group.length, subgroup = subgroups[j] = [], node, i = 0; i < n; ++i) if ((node = group[i]) && match.call(node, node.__data__, i, group)) subgroup.push(node);
	return new Selection$1(subgroups, this._parents);
}
//#endregion
//#region node_modules/d3-selection/src/selection/sparse.js
function sparse_default(update) {
	return new Array(update.length);
}
//#endregion
//#region node_modules/d3-selection/src/selection/enter.js
function enter_default() {
	return new Selection$1(this._enter || this._groups.map(sparse_default), this._parents);
}
function EnterNode(parent, datum) {
	this.ownerDocument = parent.ownerDocument;
	this.namespaceURI = parent.namespaceURI;
	this._next = null;
	this._parent = parent;
	this.__data__ = datum;
}
EnterNode.prototype = {
	constructor: EnterNode,
	appendChild: function(child) {
		return this._parent.insertBefore(child, this._next);
	},
	insertBefore: function(child, next) {
		return this._parent.insertBefore(child, next);
	},
	querySelector: function(selector) {
		return this._parent.querySelector(selector);
	},
	querySelectorAll: function(selector) {
		return this._parent.querySelectorAll(selector);
	}
};
//#endregion
//#region node_modules/d3-selection/src/constant.js
function constant_default$3(x) {
	return function() {
		return x;
	};
}
//#endregion
//#region node_modules/d3-selection/src/selection/data.js
function bindIndex(parent, group, enter, update, exit, data) {
	var i = 0, node, groupLength = group.length, dataLength = data.length;
	for (; i < dataLength; ++i) if (node = group[i]) {
		node.__data__ = data[i];
		update[i] = node;
	} else enter[i] = new EnterNode(parent, data[i]);
	for (; i < groupLength; ++i) if (node = group[i]) exit[i] = node;
}
function bindKey(parent, group, enter, update, exit, data, key) {
	var i, node, nodeByKeyValue = /* @__PURE__ */ new Map(), groupLength = group.length, dataLength = data.length, keyValues = new Array(groupLength), keyValue;
	for (i = 0; i < groupLength; ++i) if (node = group[i]) {
		keyValues[i] = keyValue = key.call(node, node.__data__, i, group) + "";
		if (nodeByKeyValue.has(keyValue)) exit[i] = node;
		else nodeByKeyValue.set(keyValue, node);
	}
	for (i = 0; i < dataLength; ++i) {
		keyValue = key.call(parent, data[i], i, data) + "";
		if (node = nodeByKeyValue.get(keyValue)) {
			update[i] = node;
			node.__data__ = data[i];
			nodeByKeyValue.delete(keyValue);
		} else enter[i] = new EnterNode(parent, data[i]);
	}
	for (i = 0; i < groupLength; ++i) if ((node = group[i]) && nodeByKeyValue.get(keyValues[i]) === node) exit[i] = node;
}
function datum(node) {
	return node.__data__;
}
function data_default(value, key) {
	if (!arguments.length) return Array.from(this, datum);
	var bind = key ? bindKey : bindIndex, parents = this._parents, groups = this._groups;
	if (typeof value !== "function") value = constant_default$3(value);
	for (var m = groups.length, update = new Array(m), enter = new Array(m), exit = new Array(m), j = 0; j < m; ++j) {
		var parent = parents[j], group = groups[j], groupLength = group.length, data = arraylike(value.call(parent, parent && parent.__data__, j, parents)), dataLength = data.length, enterGroup = enter[j] = new Array(dataLength), updateGroup = update[j] = new Array(dataLength);
		bind(parent, group, enterGroup, updateGroup, exit[j] = new Array(groupLength), data, key);
		for (var i0 = 0, i1 = 0, previous, next; i0 < dataLength; ++i0) if (previous = enterGroup[i0]) {
			if (i0 >= i1) i1 = i0 + 1;
			while (!(next = updateGroup[i1]) && ++i1 < dataLength);
			previous._next = next || null;
		}
	}
	update = new Selection$1(update, parents);
	update._enter = enter;
	update._exit = exit;
	return update;
}
function arraylike(data) {
	return typeof data === "object" && "length" in data ? data : Array.from(data);
}
//#endregion
//#region node_modules/d3-selection/src/selection/exit.js
function exit_default() {
	return new Selection$1(this._exit || this._groups.map(sparse_default), this._parents);
}
//#endregion
//#region node_modules/d3-selection/src/selection/join.js
function join_default(onenter, onupdate, onexit) {
	var enter = this.enter(), update = this, exit = this.exit();
	if (typeof onenter === "function") {
		enter = onenter(enter);
		if (enter) enter = enter.selection();
	} else enter = enter.append(onenter + "");
	if (onupdate != null) {
		update = onupdate(update);
		if (update) update = update.selection();
	}
	if (onexit == null) exit.remove();
	else onexit(exit);
	return enter && update ? enter.merge(update).order() : update;
}
//#endregion
//#region node_modules/d3-selection/src/selection/merge.js
function merge_default$1(context) {
	var selection = context.selection ? context.selection() : context;
	for (var groups0 = this._groups, groups1 = selection._groups, m0 = groups0.length, m1 = groups1.length, m = Math.min(m0, m1), merges = new Array(m0), j = 0; j < m; ++j) for (var group0 = groups0[j], group1 = groups1[j], n = group0.length, merge = merges[j] = new Array(n), node, i = 0; i < n; ++i) if (node = group0[i] || group1[i]) merge[i] = node;
	for (; j < m0; ++j) merges[j] = groups0[j];
	return new Selection$1(merges, this._parents);
}
//#endregion
//#region node_modules/d3-selection/src/selection/order.js
function order_default() {
	for (var groups = this._groups, j = -1, m = groups.length; ++j < m;) for (var group = groups[j], i = group.length - 1, next = group[i], node; --i >= 0;) if (node = group[i]) {
		if (next && node.compareDocumentPosition(next) ^ 4) next.parentNode.insertBefore(node, next);
		next = node;
	}
	return this;
}
//#endregion
//#region node_modules/d3-selection/src/selection/sort.js
function sort_default(compare) {
	if (!compare) compare = ascending;
	function compareNode(a, b) {
		return a && b ? compare(a.__data__, b.__data__) : !a - !b;
	}
	for (var groups = this._groups, m = groups.length, sortgroups = new Array(m), j = 0; j < m; ++j) {
		for (var group = groups[j], n = group.length, sortgroup = sortgroups[j] = new Array(n), node, i = 0; i < n; ++i) if (node = group[i]) sortgroup[i] = node;
		sortgroup.sort(compareNode);
	}
	return new Selection$1(sortgroups, this._parents).order();
}
function ascending(a, b) {
	return a < b ? -1 : a > b ? 1 : a >= b ? 0 : NaN;
}
//#endregion
//#region node_modules/d3-selection/src/selection/call.js
function call_default() {
	var callback = arguments[0];
	arguments[0] = this;
	callback.apply(null, arguments);
	return this;
}
//#endregion
//#region node_modules/d3-selection/src/selection/nodes.js
function nodes_default() {
	return Array.from(this);
}
//#endregion
//#region node_modules/d3-selection/src/selection/node.js
function node_default() {
	for (var groups = this._groups, j = 0, m = groups.length; j < m; ++j) for (var group = groups[j], i = 0, n = group.length; i < n; ++i) {
		var node = group[i];
		if (node) return node;
	}
	return null;
}
//#endregion
//#region node_modules/d3-selection/src/selection/size.js
function size_default() {
	let size = 0;
	for (const node of this) ++size;
	return size;
}
//#endregion
//#region node_modules/d3-selection/src/selection/empty.js
function empty_default() {
	return !this.node();
}
//#endregion
//#region node_modules/d3-selection/src/selection/each.js
function each_default(callback) {
	for (var groups = this._groups, j = 0, m = groups.length; j < m; ++j) for (var group = groups[j], i = 0, n = group.length, node; i < n; ++i) if (node = group[i]) callback.call(node, node.__data__, i, group);
	return this;
}
//#endregion
//#region node_modules/d3-selection/src/selection/attr.js
function attrRemove$1(name) {
	return function() {
		this.removeAttribute(name);
	};
}
function attrRemoveNS$1(fullname) {
	return function() {
		this.removeAttributeNS(fullname.space, fullname.local);
	};
}
function attrConstant$1(name, value) {
	return function() {
		this.setAttribute(name, value);
	};
}
function attrConstantNS$1(fullname, value) {
	return function() {
		this.setAttributeNS(fullname.space, fullname.local, value);
	};
}
function attrFunction$1(name, value) {
	return function() {
		var v = value.apply(this, arguments);
		if (v == null) this.removeAttribute(name);
		else this.setAttribute(name, v);
	};
}
function attrFunctionNS$1(fullname, value) {
	return function() {
		var v = value.apply(this, arguments);
		if (v == null) this.removeAttributeNS(fullname.space, fullname.local);
		else this.setAttributeNS(fullname.space, fullname.local, v);
	};
}
function attr_default$1(name, value) {
	var fullname = namespace_default(name);
	if (arguments.length < 2) {
		var node = this.node();
		return fullname.local ? node.getAttributeNS(fullname.space, fullname.local) : node.getAttribute(fullname);
	}
	return this.each((value == null ? fullname.local ? attrRemoveNS$1 : attrRemove$1 : typeof value === "function" ? fullname.local ? attrFunctionNS$1 : attrFunction$1 : fullname.local ? attrConstantNS$1 : attrConstant$1)(fullname, value));
}
//#endregion
//#region node_modules/d3-selection/src/window.js
function window_default(node) {
	return node.ownerDocument && node.ownerDocument.defaultView || node.document && node || node.defaultView;
}
//#endregion
//#region node_modules/d3-selection/src/selection/style.js
function styleRemove$1(name) {
	return function() {
		this.style.removeProperty(name);
	};
}
function styleConstant$1(name, value, priority) {
	return function() {
		this.style.setProperty(name, value, priority);
	};
}
function styleFunction$1(name, value, priority) {
	return function() {
		var v = value.apply(this, arguments);
		if (v == null) this.style.removeProperty(name);
		else this.style.setProperty(name, v, priority);
	};
}
function style_default$1(name, value, priority) {
	return arguments.length > 1 ? this.each((value == null ? styleRemove$1 : typeof value === "function" ? styleFunction$1 : styleConstant$1)(name, value, priority == null ? "" : priority)) : styleValue(this.node(), name);
}
function styleValue(node, name) {
	return node.style.getPropertyValue(name) || window_default(node).getComputedStyle(node, null).getPropertyValue(name);
}
//#endregion
//#region node_modules/d3-selection/src/selection/property.js
function propertyRemove(name) {
	return function() {
		delete this[name];
	};
}
function propertyConstant(name, value) {
	return function() {
		this[name] = value;
	};
}
function propertyFunction(name, value) {
	return function() {
		var v = value.apply(this, arguments);
		if (v == null) delete this[name];
		else this[name] = v;
	};
}
function property_default(name, value) {
	return arguments.length > 1 ? this.each((value == null ? propertyRemove : typeof value === "function" ? propertyFunction : propertyConstant)(name, value)) : this.node()[name];
}
//#endregion
//#region node_modules/d3-selection/src/selection/classed.js
function classArray(string) {
	return string.trim().split(/^|\s+/);
}
function classList(node) {
	return node.classList || new ClassList(node);
}
function ClassList(node) {
	this._node = node;
	this._names = classArray(node.getAttribute("class") || "");
}
ClassList.prototype = {
	add: function(name) {
		if (this._names.indexOf(name) < 0) {
			this._names.push(name);
			this._node.setAttribute("class", this._names.join(" "));
		}
	},
	remove: function(name) {
		var i = this._names.indexOf(name);
		if (i >= 0) {
			this._names.splice(i, 1);
			this._node.setAttribute("class", this._names.join(" "));
		}
	},
	contains: function(name) {
		return this._names.indexOf(name) >= 0;
	}
};
function classedAdd(node, names) {
	var list = classList(node), i = -1, n = names.length;
	while (++i < n) list.add(names[i]);
}
function classedRemove(node, names) {
	var list = classList(node), i = -1, n = names.length;
	while (++i < n) list.remove(names[i]);
}
function classedTrue(names) {
	return function() {
		classedAdd(this, names);
	};
}
function classedFalse(names) {
	return function() {
		classedRemove(this, names);
	};
}
function classedFunction(names, value) {
	return function() {
		(value.apply(this, arguments) ? classedAdd : classedRemove)(this, names);
	};
}
function classed_default(name, value) {
	var names = classArray(name + "");
	if (arguments.length < 2) {
		var list = classList(this.node()), i = -1, n = names.length;
		while (++i < n) if (!list.contains(names[i])) return false;
		return true;
	}
	return this.each((typeof value === "function" ? classedFunction : value ? classedTrue : classedFalse)(names, value));
}
//#endregion
//#region node_modules/d3-selection/src/selection/text.js
function textRemove() {
	this.textContent = "";
}
function textConstant$1(value) {
	return function() {
		this.textContent = value;
	};
}
function textFunction$1(value) {
	return function() {
		var v = value.apply(this, arguments);
		this.textContent = v == null ? "" : v;
	};
}
function text_default$1(value) {
	return arguments.length ? this.each(value == null ? textRemove : (typeof value === "function" ? textFunction$1 : textConstant$1)(value)) : this.node().textContent;
}
//#endregion
//#region node_modules/d3-selection/src/selection/html.js
function htmlRemove() {
	this.innerHTML = "";
}
function htmlConstant(value) {
	return function() {
		this.innerHTML = value;
	};
}
function htmlFunction(value) {
	return function() {
		var v = value.apply(this, arguments);
		this.innerHTML = v == null ? "" : v;
	};
}
function html_default(value) {
	return arguments.length ? this.each(value == null ? htmlRemove : (typeof value === "function" ? htmlFunction : htmlConstant)(value)) : this.node().innerHTML;
}
//#endregion
//#region node_modules/d3-selection/src/selection/raise.js
function raise() {
	if (this.nextSibling) this.parentNode.appendChild(this);
}
function raise_default() {
	return this.each(raise);
}
//#endregion
//#region node_modules/d3-selection/src/selection/lower.js
function lower() {
	if (this.previousSibling) this.parentNode.insertBefore(this, this.parentNode.firstChild);
}
function lower_default() {
	return this.each(lower);
}
//#endregion
//#region node_modules/d3-selection/src/selection/append.js
function append_default(name) {
	var create = typeof name === "function" ? name : creator_default(name);
	return this.select(function() {
		return this.appendChild(create.apply(this, arguments));
	});
}
//#endregion
//#region node_modules/d3-selection/src/selection/insert.js
function constantNull() {
	return null;
}
function insert_default(name, before) {
	var create = typeof name === "function" ? name : creator_default(name), select = before == null ? constantNull : typeof before === "function" ? before : selector_default(before);
	return this.select(function() {
		return this.insertBefore(create.apply(this, arguments), select.apply(this, arguments) || null);
	});
}
//#endregion
//#region node_modules/d3-selection/src/selection/remove.js
function remove() {
	var parent = this.parentNode;
	if (parent) parent.removeChild(this);
}
function remove_default$1() {
	return this.each(remove);
}
//#endregion
//#region node_modules/d3-selection/src/selection/clone.js
function selection_cloneShallow() {
	var clone = this.cloneNode(false), parent = this.parentNode;
	return parent ? parent.insertBefore(clone, this.nextSibling) : clone;
}
function selection_cloneDeep() {
	var clone = this.cloneNode(true), parent = this.parentNode;
	return parent ? parent.insertBefore(clone, this.nextSibling) : clone;
}
function clone_default(deep) {
	return this.select(deep ? selection_cloneDeep : selection_cloneShallow);
}
//#endregion
//#region node_modules/d3-selection/src/selection/datum.js
function datum_default(value) {
	return arguments.length ? this.property("__data__", value) : this.node().__data__;
}
//#endregion
//#region node_modules/d3-selection/src/selection/on.js
function contextListener(listener) {
	return function(event) {
		listener.call(this, event, this.__data__);
	};
}
function parseTypenames(typenames) {
	return typenames.trim().split(/^|\s+/).map(function(t) {
		var name = "", i = t.indexOf(".");
		if (i >= 0) name = t.slice(i + 1), t = t.slice(0, i);
		return {
			type: t,
			name
		};
	});
}
function onRemove(typename) {
	return function() {
		var on = this.__on;
		if (!on) return;
		for (var j = 0, i = -1, m = on.length, o; j < m; ++j) if (o = on[j], (!typename.type || o.type === typename.type) && o.name === typename.name) this.removeEventListener(o.type, o.listener, o.options);
		else on[++i] = o;
		if (++i) on.length = i;
		else delete this.__on;
	};
}
function onAdd(typename, value, options) {
	return function() {
		var on = this.__on, o, listener = contextListener(value);
		if (on) {
			for (var j = 0, m = on.length; j < m; ++j) if ((o = on[j]).type === typename.type && o.name === typename.name) {
				this.removeEventListener(o.type, o.listener, o.options);
				this.addEventListener(o.type, o.listener = listener, o.options = options);
				o.value = value;
				return;
			}
		}
		this.addEventListener(typename.type, listener, options);
		o = {
			type: typename.type,
			name: typename.name,
			value,
			listener,
			options
		};
		if (!on) this.__on = [o];
		else on.push(o);
	};
}
function on_default$1(typename, value, options) {
	var typenames = parseTypenames(typename + ""), i, n = typenames.length, t;
	if (arguments.length < 2) {
		var on = this.node().__on;
		if (on) {
			for (var j = 0, m = on.length, o; j < m; ++j) for (i = 0, o = on[j]; i < n; ++i) if ((t = typenames[i]).type === o.type && t.name === o.name) return o.value;
		}
		return;
	}
	on = value ? onAdd : onRemove;
	for (i = 0; i < n; ++i) this.each(on(typenames[i], value, options));
	return this;
}
//#endregion
//#region node_modules/d3-selection/src/selection/dispatch.js
function dispatchEvent(node, type, params) {
	var window = window_default(node), event = window.CustomEvent;
	if (typeof event === "function") event = new event(type, params);
	else {
		event = window.document.createEvent("Event");
		if (params) event.initEvent(type, params.bubbles, params.cancelable), event.detail = params.detail;
		else event.initEvent(type, false, false);
	}
	node.dispatchEvent(event);
}
function dispatchConstant(type, params) {
	return function() {
		return dispatchEvent(this, type, params);
	};
}
function dispatchFunction(type, params) {
	return function() {
		return dispatchEvent(this, type, params.apply(this, arguments));
	};
}
function dispatch_default(type, params) {
	return this.each((typeof params === "function" ? dispatchFunction : dispatchConstant)(type, params));
}
//#endregion
//#region node_modules/d3-selection/src/selection/iterator.js
function* iterator_default() {
	for (var groups = this._groups, j = 0, m = groups.length; j < m; ++j) for (var group = groups[j], i = 0, n = group.length, node; i < n; ++i) if (node = group[i]) yield node;
}
//#endregion
//#region node_modules/d3-selection/src/selection/index.js
var root = [null];
function Selection$1(groups, parents) {
	this._groups = groups;
	this._parents = parents;
}
function selection() {
	return new Selection$1([[document.documentElement]], root);
}
function selection_selection() {
	return this;
}
Selection$1.prototype = selection.prototype = {
	constructor: Selection$1,
	select: select_default$2,
	selectAll: selectAll_default$1,
	selectChild: selectChild_default,
	selectChildren: selectChildren_default,
	filter: filter_default$1,
	data: data_default,
	enter: enter_default,
	exit: exit_default,
	join: join_default,
	merge: merge_default$1,
	selection: selection_selection,
	order: order_default,
	sort: sort_default,
	call: call_default,
	nodes: nodes_default,
	node: node_default,
	size: size_default,
	empty: empty_default,
	each: each_default,
	attr: attr_default$1,
	style: style_default$1,
	property: property_default,
	classed: classed_default,
	text: text_default$1,
	html: html_default,
	raise: raise_default,
	lower: lower_default,
	append: append_default,
	insert: insert_default,
	remove: remove_default$1,
	clone: clone_default,
	datum: datum_default,
	on: on_default$1,
	dispatch: dispatch_default,
	[Symbol.iterator]: iterator_default
};
//#endregion
//#region node_modules/d3-selection/src/select.js
function select_default$1(selector) {
	return typeof selector === "string" ? new Selection$1([[document.querySelector(selector)]], [document.documentElement]) : new Selection$1([[selector]], root);
}
//#endregion
//#region node_modules/d3-selection/src/sourceEvent.js
function sourceEvent_default(event) {
	let sourceEvent;
	while (sourceEvent = event.sourceEvent) event = sourceEvent;
	return event;
}
//#endregion
//#region node_modules/d3-selection/src/pointer.js
function pointer_default(event, node) {
	event = sourceEvent_default(event);
	if (node === void 0) node = event.currentTarget;
	if (node) {
		var svg = node.ownerSVGElement || node;
		if (svg.createSVGPoint) {
			var point = svg.createSVGPoint();
			point.x = event.clientX, point.y = event.clientY;
			point = point.matrixTransform(node.getScreenCTM().inverse());
			return [point.x, point.y];
		}
		if (node.getBoundingClientRect) {
			var rect = node.getBoundingClientRect();
			return [event.clientX - rect.left - node.clientLeft, event.clientY - rect.top - node.clientTop];
		}
	}
	return [event.pageX, event.pageY];
}
//#endregion
//#region node_modules/d3-drag/src/noevent.js
var nonpassive = { passive: false };
var nonpassivecapture = {
	capture: true,
	passive: false
};
function nopropagation$1(event) {
	event.stopImmediatePropagation();
}
function noevent_default$1(event) {
	event.preventDefault();
	event.stopImmediatePropagation();
}
//#endregion
//#region node_modules/d3-drag/src/nodrag.js
function nodrag_default(view) {
	var root = view.document.documentElement, selection = select_default$1(view).on("dragstart.drag", noevent_default$1, nonpassivecapture);
	if ("onselectstart" in root) selection.on("selectstart.drag", noevent_default$1, nonpassivecapture);
	else {
		root.__noselect = root.style.MozUserSelect;
		root.style.MozUserSelect = "none";
	}
}
function yesdrag(view, noclick) {
	var root = view.document.documentElement, selection = select_default$1(view).on("dragstart.drag", null);
	if (noclick) {
		selection.on("click.drag", noevent_default$1, nonpassivecapture);
		setTimeout(function() {
			selection.on("click.drag", null);
		}, 0);
	}
	if ("onselectstart" in root) selection.on("selectstart.drag", null);
	else {
		root.style.MozUserSelect = root.__noselect;
		delete root.__noselect;
	}
}
//#endregion
//#region node_modules/d3-drag/src/constant.js
var constant_default$2 = (x) => () => x;
//#endregion
//#region node_modules/d3-drag/src/event.js
function DragEvent(type, { sourceEvent, subject, target, identifier, active, x, y, dx, dy, dispatch }) {
	Object.defineProperties(this, {
		type: {
			value: type,
			enumerable: true,
			configurable: true
		},
		sourceEvent: {
			value: sourceEvent,
			enumerable: true,
			configurable: true
		},
		subject: {
			value: subject,
			enumerable: true,
			configurable: true
		},
		target: {
			value: target,
			enumerable: true,
			configurable: true
		},
		identifier: {
			value: identifier,
			enumerable: true,
			configurable: true
		},
		active: {
			value: active,
			enumerable: true,
			configurable: true
		},
		x: {
			value: x,
			enumerable: true,
			configurable: true
		},
		y: {
			value: y,
			enumerable: true,
			configurable: true
		},
		dx: {
			value: dx,
			enumerable: true,
			configurable: true
		},
		dy: {
			value: dy,
			enumerable: true,
			configurable: true
		},
		_: { value: dispatch }
	});
}
DragEvent.prototype.on = function() {
	var value = this._.on.apply(this._, arguments);
	return value === this._ ? this : value;
};
//#endregion
//#region node_modules/d3-drag/src/drag.js
function defaultFilter$1(event) {
	return !event.ctrlKey && !event.button;
}
function defaultContainer() {
	return this.parentNode;
}
function defaultSubject(event, d) {
	return d == null ? {
		x: event.x,
		y: event.y
	} : d;
}
function defaultTouchable$1() {
	return navigator.maxTouchPoints || "ontouchstart" in this;
}
function drag_default() {
	var filter = defaultFilter$1, container = defaultContainer, subject = defaultSubject, touchable = defaultTouchable$1, gestures = {}, listeners = dispatch("start", "drag", "end"), active = 0, mousedownx, mousedowny, mousemoving, touchending, clickDistance2 = 0;
	function drag(selection) {
		selection.on("mousedown.drag", mousedowned).filter(touchable).on("touchstart.drag", touchstarted).on("touchmove.drag", touchmoved, nonpassive).on("touchend.drag touchcancel.drag", touchended).style("touch-action", "none").style("-webkit-tap-highlight-color", "rgba(0,0,0,0)");
	}
	function mousedowned(event, d) {
		if (touchending || !filter.call(this, event, d)) return;
		var gesture = beforestart(this, container.call(this, event, d), event, d, "mouse");
		if (!gesture) return;
		select_default$1(event.view).on("mousemove.drag", mousemoved, nonpassivecapture).on("mouseup.drag", mouseupped, nonpassivecapture);
		nodrag_default(event.view);
		nopropagation$1(event);
		mousemoving = false;
		mousedownx = event.clientX;
		mousedowny = event.clientY;
		gesture("start", event);
	}
	function mousemoved(event) {
		noevent_default$1(event);
		if (!mousemoving) {
			var dx = event.clientX - mousedownx, dy = event.clientY - mousedowny;
			mousemoving = dx * dx + dy * dy > clickDistance2;
		}
		gestures.mouse("drag", event);
	}
	function mouseupped(event) {
		select_default$1(event.view).on("mousemove.drag mouseup.drag", null);
		yesdrag(event.view, mousemoving);
		noevent_default$1(event);
		gestures.mouse("end", event);
	}
	function touchstarted(event, d) {
		if (!filter.call(this, event, d)) return;
		var touches = event.changedTouches, c = container.call(this, event, d), n = touches.length, i, gesture;
		for (i = 0; i < n; ++i) if (gesture = beforestart(this, c, event, d, touches[i].identifier, touches[i])) {
			nopropagation$1(event);
			gesture("start", event, touches[i]);
		}
	}
	function touchmoved(event) {
		var touches = event.changedTouches, n = touches.length, i, gesture;
		for (i = 0; i < n; ++i) if (gesture = gestures[touches[i].identifier]) {
			noevent_default$1(event);
			gesture("drag", event, touches[i]);
		}
	}
	function touchended(event) {
		var touches = event.changedTouches, n = touches.length, i, gesture;
		if (touchending) clearTimeout(touchending);
		touchending = setTimeout(function() {
			touchending = null;
		}, 500);
		for (i = 0; i < n; ++i) if (gesture = gestures[touches[i].identifier]) {
			nopropagation$1(event);
			gesture("end", event, touches[i]);
		}
	}
	function beforestart(that, container, event, d, identifier, touch) {
		var dispatch = listeners.copy(), p = pointer_default(touch || event, container), dx, dy, s;
		if ((s = subject.call(that, new DragEvent("beforestart", {
			sourceEvent: event,
			target: drag,
			identifier,
			active,
			x: p[0],
			y: p[1],
			dx: 0,
			dy: 0,
			dispatch
		}), d)) == null) return;
		dx = s.x - p[0] || 0;
		dy = s.y - p[1] || 0;
		return function gesture(type, event, touch) {
			var p0 = p, n;
			switch (type) {
				case "start":
					gestures[identifier] = gesture, n = active++;
					break;
				case "end": delete gestures[identifier], --active;
				case "drag":
					p = pointer_default(touch || event, container), n = active;
					break;
			}
			dispatch.call(type, that, new DragEvent(type, {
				sourceEvent: event,
				subject: s,
				target: drag,
				identifier,
				active: n,
				x: p[0] + dx,
				y: p[1] + dy,
				dx: p[0] - p0[0],
				dy: p[1] - p0[1],
				dispatch
			}), d);
		};
	}
	drag.filter = function(_) {
		return arguments.length ? (filter = typeof _ === "function" ? _ : constant_default$2(!!_), drag) : filter;
	};
	drag.container = function(_) {
		return arguments.length ? (container = typeof _ === "function" ? _ : constant_default$2(_), drag) : container;
	};
	drag.subject = function(_) {
		return arguments.length ? (subject = typeof _ === "function" ? _ : constant_default$2(_), drag) : subject;
	};
	drag.touchable = function(_) {
		return arguments.length ? (touchable = typeof _ === "function" ? _ : constant_default$2(!!_), drag) : touchable;
	};
	drag.on = function() {
		var value = listeners.on.apply(listeners, arguments);
		return value === listeners ? drag : value;
	};
	drag.clickDistance = function(_) {
		return arguments.length ? (clickDistance2 = (_ = +_) * _, drag) : Math.sqrt(clickDistance2);
	};
	return drag;
}
//#endregion
//#region node_modules/d3-color/src/define.js
function define_default(constructor, factory, prototype) {
	constructor.prototype = factory.prototype = prototype;
	prototype.constructor = constructor;
}
function extend(parent, definition) {
	var prototype = Object.create(parent.prototype);
	for (var key in definition) prototype[key] = definition[key];
	return prototype;
}
//#endregion
//#region node_modules/d3-color/src/color.js
function Color() {}
var darker = .7;
var brighter = 1 / darker;
var reI = "\\s*([+-]?\\d+)\\s*", reN = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*", reP = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*", reHex = /^#([0-9a-f]{3,8})$/, reRgbInteger = new RegExp(`^rgb\\(${reI},${reI},${reI}\\)$`), reRgbPercent = new RegExp(`^rgb\\(${reP},${reP},${reP}\\)$`), reRgbaInteger = new RegExp(`^rgba\\(${reI},${reI},${reI},${reN}\\)$`), reRgbaPercent = new RegExp(`^rgba\\(${reP},${reP},${reP},${reN}\\)$`), reHslPercent = new RegExp(`^hsl\\(${reN},${reP},${reP}\\)$`), reHslaPercent = new RegExp(`^hsla\\(${reN},${reP},${reP},${reN}\\)$`);
var named = {
	aliceblue: 15792383,
	antiquewhite: 16444375,
	aqua: 65535,
	aquamarine: 8388564,
	azure: 15794175,
	beige: 16119260,
	bisque: 16770244,
	black: 0,
	blanchedalmond: 16772045,
	blue: 255,
	blueviolet: 9055202,
	brown: 10824234,
	burlywood: 14596231,
	cadetblue: 6266528,
	chartreuse: 8388352,
	chocolate: 13789470,
	coral: 16744272,
	cornflowerblue: 6591981,
	cornsilk: 16775388,
	crimson: 14423100,
	cyan: 65535,
	darkblue: 139,
	darkcyan: 35723,
	darkgoldenrod: 12092939,
	darkgray: 11119017,
	darkgreen: 25600,
	darkgrey: 11119017,
	darkkhaki: 12433259,
	darkmagenta: 9109643,
	darkolivegreen: 5597999,
	darkorange: 16747520,
	darkorchid: 10040012,
	darkred: 9109504,
	darksalmon: 15308410,
	darkseagreen: 9419919,
	darkslateblue: 4734347,
	darkslategray: 3100495,
	darkslategrey: 3100495,
	darkturquoise: 52945,
	darkviolet: 9699539,
	deeppink: 16716947,
	deepskyblue: 49151,
	dimgray: 6908265,
	dimgrey: 6908265,
	dodgerblue: 2003199,
	firebrick: 11674146,
	floralwhite: 16775920,
	forestgreen: 2263842,
	fuchsia: 16711935,
	gainsboro: 14474460,
	ghostwhite: 16316671,
	gold: 16766720,
	goldenrod: 14329120,
	gray: 8421504,
	green: 32768,
	greenyellow: 11403055,
	grey: 8421504,
	honeydew: 15794160,
	hotpink: 16738740,
	indianred: 13458524,
	indigo: 4915330,
	ivory: 16777200,
	khaki: 15787660,
	lavender: 15132410,
	lavenderblush: 16773365,
	lawngreen: 8190976,
	lemonchiffon: 16775885,
	lightblue: 11393254,
	lightcoral: 15761536,
	lightcyan: 14745599,
	lightgoldenrodyellow: 16448210,
	lightgray: 13882323,
	lightgreen: 9498256,
	lightgrey: 13882323,
	lightpink: 16758465,
	lightsalmon: 16752762,
	lightseagreen: 2142890,
	lightskyblue: 8900346,
	lightslategray: 7833753,
	lightslategrey: 7833753,
	lightsteelblue: 11584734,
	lightyellow: 16777184,
	lime: 65280,
	limegreen: 3329330,
	linen: 16445670,
	magenta: 16711935,
	maroon: 8388608,
	mediumaquamarine: 6737322,
	mediumblue: 205,
	mediumorchid: 12211667,
	mediumpurple: 9662683,
	mediumseagreen: 3978097,
	mediumslateblue: 8087790,
	mediumspringgreen: 64154,
	mediumturquoise: 4772300,
	mediumvioletred: 13047173,
	midnightblue: 1644912,
	mintcream: 16121850,
	mistyrose: 16770273,
	moccasin: 16770229,
	navajowhite: 16768685,
	navy: 128,
	oldlace: 16643558,
	olive: 8421376,
	olivedrab: 7048739,
	orange: 16753920,
	orangered: 16729344,
	orchid: 14315734,
	palegoldenrod: 15657130,
	palegreen: 10025880,
	paleturquoise: 11529966,
	palevioletred: 14381203,
	papayawhip: 16773077,
	peachpuff: 16767673,
	peru: 13468991,
	pink: 16761035,
	plum: 14524637,
	powderblue: 11591910,
	purple: 8388736,
	rebeccapurple: 6697881,
	red: 16711680,
	rosybrown: 12357519,
	royalblue: 4286945,
	saddlebrown: 9127187,
	salmon: 16416882,
	sandybrown: 16032864,
	seagreen: 3050327,
	seashell: 16774638,
	sienna: 10506797,
	silver: 12632256,
	skyblue: 8900331,
	slateblue: 6970061,
	slategray: 7372944,
	slategrey: 7372944,
	snow: 16775930,
	springgreen: 65407,
	steelblue: 4620980,
	tan: 13808780,
	teal: 32896,
	thistle: 14204888,
	tomato: 16737095,
	turquoise: 4251856,
	violet: 15631086,
	wheat: 16113331,
	white: 16777215,
	whitesmoke: 16119285,
	yellow: 16776960,
	yellowgreen: 10145074
};
define_default(Color, color, {
	copy(channels) {
		return Object.assign(new this.constructor(), this, channels);
	},
	displayable() {
		return this.rgb().displayable();
	},
	hex: color_formatHex,
	formatHex: color_formatHex,
	formatHex8: color_formatHex8,
	formatHsl: color_formatHsl,
	formatRgb: color_formatRgb,
	toString: color_formatRgb
});
function color_formatHex() {
	return this.rgb().formatHex();
}
function color_formatHex8() {
	return this.rgb().formatHex8();
}
function color_formatHsl() {
	return hslConvert(this).formatHsl();
}
function color_formatRgb() {
	return this.rgb().formatRgb();
}
function color(format) {
	var m, l;
	format = (format + "").trim().toLowerCase();
	return (m = reHex.exec(format)) ? (l = m[1].length, m = parseInt(m[1], 16), l === 6 ? rgbn(m) : l === 3 ? new Rgb(m >> 8 & 15 | m >> 4 & 240, m >> 4 & 15 | m & 240, (m & 15) << 4 | m & 15, 1) : l === 8 ? rgba(m >> 24 & 255, m >> 16 & 255, m >> 8 & 255, (m & 255) / 255) : l === 4 ? rgba(m >> 12 & 15 | m >> 8 & 240, m >> 8 & 15 | m >> 4 & 240, m >> 4 & 15 | m & 240, ((m & 15) << 4 | m & 15) / 255) : null) : (m = reRgbInteger.exec(format)) ? new Rgb(m[1], m[2], m[3], 1) : (m = reRgbPercent.exec(format)) ? new Rgb(m[1] * 255 / 100, m[2] * 255 / 100, m[3] * 255 / 100, 1) : (m = reRgbaInteger.exec(format)) ? rgba(m[1], m[2], m[3], m[4]) : (m = reRgbaPercent.exec(format)) ? rgba(m[1] * 255 / 100, m[2] * 255 / 100, m[3] * 255 / 100, m[4]) : (m = reHslPercent.exec(format)) ? hsla(m[1], m[2] / 100, m[3] / 100, 1) : (m = reHslaPercent.exec(format)) ? hsla(m[1], m[2] / 100, m[3] / 100, m[4]) : named.hasOwnProperty(format) ? rgbn(named[format]) : format === "transparent" ? new Rgb(NaN, NaN, NaN, 0) : null;
}
function rgbn(n) {
	return new Rgb(n >> 16 & 255, n >> 8 & 255, n & 255, 1);
}
function rgba(r, g, b, a) {
	if (a <= 0) r = g = b = NaN;
	return new Rgb(r, g, b, a);
}
function rgbConvert(o) {
	if (!(o instanceof Color)) o = color(o);
	if (!o) return new Rgb();
	o = o.rgb();
	return new Rgb(o.r, o.g, o.b, o.opacity);
}
function rgb(r, g, b, opacity) {
	return arguments.length === 1 ? rgbConvert(r) : new Rgb(r, g, b, opacity == null ? 1 : opacity);
}
function Rgb(r, g, b, opacity) {
	this.r = +r;
	this.g = +g;
	this.b = +b;
	this.opacity = +opacity;
}
define_default(Rgb, rgb, extend(Color, {
	brighter(k) {
		k = k == null ? brighter : Math.pow(brighter, k);
		return new Rgb(this.r * k, this.g * k, this.b * k, this.opacity);
	},
	darker(k) {
		k = k == null ? darker : Math.pow(darker, k);
		return new Rgb(this.r * k, this.g * k, this.b * k, this.opacity);
	},
	rgb() {
		return this;
	},
	clamp() {
		return new Rgb(clampi(this.r), clampi(this.g), clampi(this.b), clampa(this.opacity));
	},
	displayable() {
		return -.5 <= this.r && this.r < 255.5 && -.5 <= this.g && this.g < 255.5 && -.5 <= this.b && this.b < 255.5 && 0 <= this.opacity && this.opacity <= 1;
	},
	hex: rgb_formatHex,
	formatHex: rgb_formatHex,
	formatHex8: rgb_formatHex8,
	formatRgb: rgb_formatRgb,
	toString: rgb_formatRgb
}));
function rgb_formatHex() {
	return `#${hex(this.r)}${hex(this.g)}${hex(this.b)}`;
}
function rgb_formatHex8() {
	return `#${hex(this.r)}${hex(this.g)}${hex(this.b)}${hex((isNaN(this.opacity) ? 1 : this.opacity) * 255)}`;
}
function rgb_formatRgb() {
	const a = clampa(this.opacity);
	return `${a === 1 ? "rgb(" : "rgba("}${clampi(this.r)}, ${clampi(this.g)}, ${clampi(this.b)}${a === 1 ? ")" : `, ${a})`}`;
}
function clampa(opacity) {
	return isNaN(opacity) ? 1 : Math.max(0, Math.min(1, opacity));
}
function clampi(value) {
	return Math.max(0, Math.min(255, Math.round(value) || 0));
}
function hex(value) {
	value = clampi(value);
	return (value < 16 ? "0" : "") + value.toString(16);
}
function hsla(h, s, l, a) {
	if (a <= 0) h = s = l = NaN;
	else if (l <= 0 || l >= 1) h = s = NaN;
	else if (s <= 0) h = NaN;
	return new Hsl(h, s, l, a);
}
function hslConvert(o) {
	if (o instanceof Hsl) return new Hsl(o.h, o.s, o.l, o.opacity);
	if (!(o instanceof Color)) o = color(o);
	if (!o) return new Hsl();
	if (o instanceof Hsl) return o;
	o = o.rgb();
	var r = o.r / 255, g = o.g / 255, b = o.b / 255, min = Math.min(r, g, b), max = Math.max(r, g, b), h = NaN, s = max - min, l = (max + min) / 2;
	if (s) {
		if (r === max) h = (g - b) / s + (g < b) * 6;
		else if (g === max) h = (b - r) / s + 2;
		else h = (r - g) / s + 4;
		s /= l < .5 ? max + min : 2 - max - min;
		h *= 60;
	} else s = l > 0 && l < 1 ? 0 : h;
	return new Hsl(h, s, l, o.opacity);
}
function hsl(h, s, l, opacity) {
	return arguments.length === 1 ? hslConvert(h) : new Hsl(h, s, l, opacity == null ? 1 : opacity);
}
function Hsl(h, s, l, opacity) {
	this.h = +h;
	this.s = +s;
	this.l = +l;
	this.opacity = +opacity;
}
define_default(Hsl, hsl, extend(Color, {
	brighter(k) {
		k = k == null ? brighter : Math.pow(brighter, k);
		return new Hsl(this.h, this.s, this.l * k, this.opacity);
	},
	darker(k) {
		k = k == null ? darker : Math.pow(darker, k);
		return new Hsl(this.h, this.s, this.l * k, this.opacity);
	},
	rgb() {
		var h = this.h % 360 + (this.h < 0) * 360, s = isNaN(h) || isNaN(this.s) ? 0 : this.s, l = this.l, m2 = l + (l < .5 ? l : 1 - l) * s, m1 = 2 * l - m2;
		return new Rgb(hsl2rgb(h >= 240 ? h - 240 : h + 120, m1, m2), hsl2rgb(h, m1, m2), hsl2rgb(h < 120 ? h + 240 : h - 120, m1, m2), this.opacity);
	},
	clamp() {
		return new Hsl(clamph(this.h), clampt(this.s), clampt(this.l), clampa(this.opacity));
	},
	displayable() {
		return (0 <= this.s && this.s <= 1 || isNaN(this.s)) && 0 <= this.l && this.l <= 1 && 0 <= this.opacity && this.opacity <= 1;
	},
	formatHsl() {
		const a = clampa(this.opacity);
		return `${a === 1 ? "hsl(" : "hsla("}${clamph(this.h)}, ${clampt(this.s) * 100}%, ${clampt(this.l) * 100}%${a === 1 ? ")" : `, ${a})`}`;
	}
}));
function clamph(value) {
	value = (value || 0) % 360;
	return value < 0 ? value + 360 : value;
}
function clampt(value) {
	return Math.max(0, Math.min(1, value || 0));
}
function hsl2rgb(h, m1, m2) {
	return (h < 60 ? m1 + (m2 - m1) * h / 60 : h < 180 ? m2 : h < 240 ? m1 + (m2 - m1) * (240 - h) / 60 : m1) * 255;
}
//#endregion
//#region node_modules/d3-interpolate/src/basis.js
function basis(t1, v0, v1, v2, v3) {
	var t2 = t1 * t1, t3 = t2 * t1;
	return ((1 - 3 * t1 + 3 * t2 - t3) * v0 + (4 - 6 * t2 + 3 * t3) * v1 + (1 + 3 * t1 + 3 * t2 - 3 * t3) * v2 + t3 * v3) / 6;
}
function basis_default(values) {
	var n = values.length - 1;
	return function(t) {
		var i = t <= 0 ? t = 0 : t >= 1 ? (t = 1, n - 1) : Math.floor(t * n), v1 = values[i], v2 = values[i + 1], v0 = i > 0 ? values[i - 1] : 2 * v1 - v2, v3 = i < n - 1 ? values[i + 2] : 2 * v2 - v1;
		return basis((t - i / n) * n, v0, v1, v2, v3);
	};
}
//#endregion
//#region node_modules/d3-interpolate/src/basisClosed.js
function basisClosed_default(values) {
	var n = values.length;
	return function(t) {
		var i = Math.floor(((t %= 1) < 0 ? ++t : t) * n), v0 = values[(i + n - 1) % n], v1 = values[i % n], v2 = values[(i + 1) % n], v3 = values[(i + 2) % n];
		return basis((t - i / n) * n, v0, v1, v2, v3);
	};
}
//#endregion
//#region node_modules/d3-interpolate/src/constant.js
var constant_default$1 = (x) => () => x;
//#endregion
//#region node_modules/d3-interpolate/src/color.js
function linear(a, d) {
	return function(t) {
		return a + t * d;
	};
}
function exponential(a, b, y) {
	return a = Math.pow(a, y), b = Math.pow(b, y) - a, y = 1 / y, function(t) {
		return Math.pow(a + t * b, y);
	};
}
function gamma(y) {
	return (y = +y) === 1 ? nogamma : function(a, b) {
		return b - a ? exponential(a, b, y) : constant_default$1(isNaN(a) ? b : a);
	};
}
function nogamma(a, b) {
	var d = b - a;
	return d ? linear(a, d) : constant_default$1(isNaN(a) ? b : a);
}
//#endregion
//#region node_modules/d3-interpolate/src/rgb.js
var rgb_default = (function rgbGamma(y) {
	var color = gamma(y);
	function rgb$1(start, end) {
		var r = color((start = rgb(start)).r, (end = rgb(end)).r), g = color(start.g, end.g), b = color(start.b, end.b), opacity = nogamma(start.opacity, end.opacity);
		return function(t) {
			start.r = r(t);
			start.g = g(t);
			start.b = b(t);
			start.opacity = opacity(t);
			return start + "";
		};
	}
	rgb$1.gamma = rgbGamma;
	return rgb$1;
})(1);
function rgbSpline(spline) {
	return function(colors) {
		var n = colors.length, r = new Array(n), g = new Array(n), b = new Array(n), i, color;
		for (i = 0; i < n; ++i) {
			color = rgb(colors[i]);
			r[i] = color.r || 0;
			g[i] = color.g || 0;
			b[i] = color.b || 0;
		}
		r = spline(r);
		g = spline(g);
		b = spline(b);
		color.opacity = 1;
		return function(t) {
			color.r = r(t);
			color.g = g(t);
			color.b = b(t);
			return color + "";
		};
	};
}
rgbSpline(basis_default);
rgbSpline(basisClosed_default);
//#endregion
//#region node_modules/d3-interpolate/src/number.js
function number_default(a, b) {
	return a = +a, b = +b, function(t) {
		return a * (1 - t) + b * t;
	};
}
//#endregion
//#region node_modules/d3-interpolate/src/string.js
var reA = /[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g, reB = new RegExp(reA.source, "g");
function zero(b) {
	return function() {
		return b;
	};
}
function one(b) {
	return function(t) {
		return b(t) + "";
	};
}
function string_default(a, b) {
	var bi = reA.lastIndex = reB.lastIndex = 0, am, bm, bs, i = -1, s = [], q = [];
	a = a + "", b = b + "";
	while ((am = reA.exec(a)) && (bm = reB.exec(b))) {
		if ((bs = bm.index) > bi) {
			bs = b.slice(bi, bs);
			if (s[i]) s[i] += bs;
			else s[++i] = bs;
		}
		if ((am = am[0]) === (bm = bm[0])) if (s[i]) s[i] += bm;
		else s[++i] = bm;
		else {
			s[++i] = null;
			q.push({
				i,
				x: number_default(am, bm)
			});
		}
		bi = reB.lastIndex;
	}
	if (bi < b.length) {
		bs = b.slice(bi);
		if (s[i]) s[i] += bs;
		else s[++i] = bs;
	}
	return s.length < 2 ? q[0] ? one(q[0].x) : zero(b) : (b = q.length, function(t) {
		for (var i = 0, o; i < b; ++i) s[(o = q[i]).i] = o.x(t);
		return s.join("");
	});
}
//#endregion
//#region node_modules/d3-interpolate/src/transform/decompose.js
var degrees = 180 / Math.PI;
var identity$1 = {
	translateX: 0,
	translateY: 0,
	rotate: 0,
	skewX: 0,
	scaleX: 1,
	scaleY: 1
};
function decompose_default(a, b, c, d, e, f) {
	var scaleX, scaleY, skewX;
	if (scaleX = Math.sqrt(a * a + b * b)) a /= scaleX, b /= scaleX;
	if (skewX = a * c + b * d) c -= a * skewX, d -= b * skewX;
	if (scaleY = Math.sqrt(c * c + d * d)) c /= scaleY, d /= scaleY, skewX /= scaleY;
	if (a * d < b * c) a = -a, b = -b, skewX = -skewX, scaleX = -scaleX;
	return {
		translateX: e,
		translateY: f,
		rotate: Math.atan2(b, a) * degrees,
		skewX: Math.atan(skewX) * degrees,
		scaleX,
		scaleY
	};
}
//#endregion
//#region node_modules/d3-interpolate/src/transform/parse.js
var svgNode;
function parseCss(value) {
	const m = new (typeof DOMMatrix === "function" ? DOMMatrix : WebKitCSSMatrix)(value + "");
	return m.isIdentity ? identity$1 : decompose_default(m.a, m.b, m.c, m.d, m.e, m.f);
}
function parseSvg(value) {
	if (value == null) return identity$1;
	if (!svgNode) svgNode = document.createElementNS("http://www.w3.org/2000/svg", "g");
	svgNode.setAttribute("transform", value);
	if (!(value = svgNode.transform.baseVal.consolidate())) return identity$1;
	value = value.matrix;
	return decompose_default(value.a, value.b, value.c, value.d, value.e, value.f);
}
//#endregion
//#region node_modules/d3-interpolate/src/transform/index.js
function interpolateTransform(parse, pxComma, pxParen, degParen) {
	function pop(s) {
		return s.length ? s.pop() + " " : "";
	}
	function translate(xa, ya, xb, yb, s, q) {
		if (xa !== xb || ya !== yb) {
			var i = s.push("translate(", null, pxComma, null, pxParen);
			q.push({
				i: i - 4,
				x: number_default(xa, xb)
			}, {
				i: i - 2,
				x: number_default(ya, yb)
			});
		} else if (xb || yb) s.push("translate(" + xb + pxComma + yb + pxParen);
	}
	function rotate(a, b, s, q) {
		if (a !== b) {
			if (a - b > 180) b += 360;
			else if (b - a > 180) a += 360;
			q.push({
				i: s.push(pop(s) + "rotate(", null, degParen) - 2,
				x: number_default(a, b)
			});
		} else if (b) s.push(pop(s) + "rotate(" + b + degParen);
	}
	function skewX(a, b, s, q) {
		if (a !== b) q.push({
			i: s.push(pop(s) + "skewX(", null, degParen) - 2,
			x: number_default(a, b)
		});
		else if (b) s.push(pop(s) + "skewX(" + b + degParen);
	}
	function scale(xa, ya, xb, yb, s, q) {
		if (xa !== xb || ya !== yb) {
			var i = s.push(pop(s) + "scale(", null, ",", null, ")");
			q.push({
				i: i - 4,
				x: number_default(xa, xb)
			}, {
				i: i - 2,
				x: number_default(ya, yb)
			});
		} else if (xb !== 1 || yb !== 1) s.push(pop(s) + "scale(" + xb + "," + yb + ")");
	}
	return function(a, b) {
		var s = [], q = [];
		a = parse(a), b = parse(b);
		translate(a.translateX, a.translateY, b.translateX, b.translateY, s, q);
		rotate(a.rotate, b.rotate, s, q);
		skewX(a.skewX, b.skewX, s, q);
		scale(a.scaleX, a.scaleY, b.scaleX, b.scaleY, s, q);
		a = b = null;
		return function(t) {
			var i = -1, n = q.length, o;
			while (++i < n) s[(o = q[i]).i] = o.x(t);
			return s.join("");
		};
	};
}
var interpolateTransformCss = interpolateTransform(parseCss, "px, ", "px)", "deg)");
var interpolateTransformSvg = interpolateTransform(parseSvg, ", ", ")", ")");
//#endregion
//#region node_modules/d3-interpolate/src/zoom.js
var epsilon2 = 1e-12;
function cosh(x) {
	return ((x = Math.exp(x)) + 1 / x) / 2;
}
function sinh(x) {
	return ((x = Math.exp(x)) - 1 / x) / 2;
}
function tanh(x) {
	return ((x = Math.exp(2 * x)) - 1) / (x + 1);
}
var zoom_default$1 = (function zoomRho(rho, rho2, rho4) {
	function zoom(p0, p1) {
		var ux0 = p0[0], uy0 = p0[1], w0 = p0[2], ux1 = p1[0], uy1 = p1[1], w1 = p1[2], dx = ux1 - ux0, dy = uy1 - uy0, d2 = dx * dx + dy * dy, i, S;
		if (d2 < epsilon2) {
			S = Math.log(w1 / w0) / rho;
			i = function(t) {
				return [
					ux0 + t * dx,
					uy0 + t * dy,
					w0 * Math.exp(rho * t * S)
				];
			};
		} else {
			var d1 = Math.sqrt(d2), b0 = (w1 * w1 - w0 * w0 + rho4 * d2) / (2 * w0 * rho2 * d1), b1 = (w1 * w1 - w0 * w0 - rho4 * d2) / (2 * w1 * rho2 * d1), r0 = Math.log(Math.sqrt(b0 * b0 + 1) - b0);
			S = (Math.log(Math.sqrt(b1 * b1 + 1) - b1) - r0) / rho;
			i = function(t) {
				var s = t * S, coshr0 = cosh(r0), u = w0 / (rho2 * d1) * (coshr0 * tanh(rho * s + r0) - sinh(r0));
				return [
					ux0 + u * dx,
					uy0 + u * dy,
					w0 * coshr0 / cosh(rho * s + r0)
				];
			};
		}
		i.duration = S * 1e3 * rho / Math.SQRT2;
		return i;
	}
	zoom.rho = function(_) {
		var _1 = Math.max(.001, +_), _2 = _1 * _1;
		return zoomRho(_1, _2, _2 * _2);
	};
	return zoom;
})(Math.SQRT2, 2, 4);
//#endregion
//#region node_modules/d3-timer/src/timer.js
var frame = 0, timeout = 0, interval = 0, pokeDelay = 1e3, taskHead, taskTail, clockLast = 0, clockNow = 0, clockSkew = 0, clock = typeof performance === "object" && performance.now ? performance : Date, setFrame = typeof window === "object" && window.requestAnimationFrame ? window.requestAnimationFrame.bind(window) : function(f) {
	setTimeout(f, 17);
};
function now() {
	return clockNow || (setFrame(clearNow), clockNow = clock.now() + clockSkew);
}
function clearNow() {
	clockNow = 0;
}
function Timer() {
	this._call = this._time = this._next = null;
}
Timer.prototype = timer.prototype = {
	constructor: Timer,
	restart: function(callback, delay, time) {
		if (typeof callback !== "function") throw new TypeError("callback is not a function");
		time = (time == null ? now() : +time) + (delay == null ? 0 : +delay);
		if (!this._next && taskTail !== this) {
			if (taskTail) taskTail._next = this;
			else taskHead = this;
			taskTail = this;
		}
		this._call = callback;
		this._time = time;
		sleep();
	},
	stop: function() {
		if (this._call) {
			this._call = null;
			this._time = Infinity;
			sleep();
		}
	}
};
function timer(callback, delay, time) {
	var t = new Timer();
	t.restart(callback, delay, time);
	return t;
}
function timerFlush() {
	now();
	++frame;
	var t = taskHead, e;
	while (t) {
		if ((e = clockNow - t._time) >= 0) t._call.call(void 0, e);
		t = t._next;
	}
	--frame;
}
function wake() {
	clockNow = (clockLast = clock.now()) + clockSkew;
	frame = timeout = 0;
	try {
		timerFlush();
	} finally {
		frame = 0;
		nap();
		clockNow = 0;
	}
}
function poke() {
	var now = clock.now(), delay = now - clockLast;
	if (delay > pokeDelay) clockSkew -= delay, clockLast = now;
}
function nap() {
	var t0, t1 = taskHead, t2, time = Infinity;
	while (t1) if (t1._call) {
		if (time > t1._time) time = t1._time;
		t0 = t1, t1 = t1._next;
	} else {
		t2 = t1._next, t1._next = null;
		t1 = t0 ? t0._next = t2 : taskHead = t2;
	}
	taskTail = t0;
	sleep(time);
}
function sleep(time) {
	if (frame) return;
	if (timeout) timeout = clearTimeout(timeout);
	if (time - clockNow > 24) {
		if (time < Infinity) timeout = setTimeout(wake, time - clock.now() - clockSkew);
		if (interval) interval = clearInterval(interval);
	} else {
		if (!interval) clockLast = clock.now(), interval = setInterval(poke, pokeDelay);
		frame = 1, setFrame(wake);
	}
}
//#endregion
//#region node_modules/d3-timer/src/timeout.js
function timeout_default(callback, delay, time) {
	var t = new Timer();
	delay = delay == null ? 0 : +delay;
	t.restart((elapsed) => {
		t.stop();
		callback(elapsed + delay);
	}, delay, time);
	return t;
}
//#endregion
//#region node_modules/d3-transition/src/transition/schedule.js
var emptyOn = dispatch("start", "end", "cancel", "interrupt");
var emptyTween = [];
function schedule_default(node, name, id, index, group, timing) {
	var schedules = node.__transition;
	if (!schedules) node.__transition = {};
	else if (id in schedules) return;
	create(node, id, {
		name,
		index,
		group,
		on: emptyOn,
		tween: emptyTween,
		time: timing.time,
		delay: timing.delay,
		duration: timing.duration,
		ease: timing.ease,
		timer: null,
		state: 0
	});
}
function init(node, id) {
	var schedule = get(node, id);
	if (schedule.state > 0) throw new Error("too late; already scheduled");
	return schedule;
}
function set(node, id) {
	var schedule = get(node, id);
	if (schedule.state > 3) throw new Error("too late; already running");
	return schedule;
}
function get(node, id) {
	var schedule = node.__transition;
	if (!schedule || !(schedule = schedule[id])) throw new Error("transition not found");
	return schedule;
}
function create(node, id, self) {
	var schedules = node.__transition, tween;
	schedules[id] = self;
	self.timer = timer(schedule, 0, self.time);
	function schedule(elapsed) {
		self.state = 1;
		self.timer.restart(start, self.delay, self.time);
		if (self.delay <= elapsed) start(elapsed - self.delay);
	}
	function start(elapsed) {
		var i, j, n, o;
		if (self.state !== 1) return stop();
		for (i in schedules) {
			o = schedules[i];
			if (o.name !== self.name) continue;
			if (o.state === 3) return timeout_default(start);
			if (o.state === 4) {
				o.state = 6;
				o.timer.stop();
				o.on.call("interrupt", node, node.__data__, o.index, o.group);
				delete schedules[i];
			} else if (+i < id) {
				o.state = 6;
				o.timer.stop();
				o.on.call("cancel", node, node.__data__, o.index, o.group);
				delete schedules[i];
			}
		}
		timeout_default(function() {
			if (self.state === 3) {
				self.state = 4;
				self.timer.restart(tick, self.delay, self.time);
				tick(elapsed);
			}
		});
		self.state = 2;
		self.on.call("start", node, node.__data__, self.index, self.group);
		if (self.state !== 2) return;
		self.state = 3;
		tween = new Array(n = self.tween.length);
		for (i = 0, j = -1; i < n; ++i) if (o = self.tween[i].value.call(node, node.__data__, self.index, self.group)) tween[++j] = o;
		tween.length = j + 1;
	}
	function tick(elapsed) {
		var t = elapsed < self.duration ? self.ease.call(null, elapsed / self.duration) : (self.timer.restart(stop), self.state = 5, 1), i = -1, n = tween.length;
		while (++i < n) tween[i].call(node, t);
		if (self.state === 5) {
			self.on.call("end", node, node.__data__, self.index, self.group);
			stop();
		}
	}
	function stop() {
		self.state = 6;
		self.timer.stop();
		delete schedules[id];
		for (var i in schedules) return;
		delete node.__transition;
	}
}
//#endregion
//#region node_modules/d3-transition/src/interrupt.js
function interrupt_default$1(node, name) {
	var schedules = node.__transition, schedule, active, empty = true, i;
	if (!schedules) return;
	name = name == null ? null : name + "";
	for (i in schedules) {
		if ((schedule = schedules[i]).name !== name) {
			empty = false;
			continue;
		}
		active = schedule.state > 2 && schedule.state < 5;
		schedule.state = 6;
		schedule.timer.stop();
		schedule.on.call(active ? "interrupt" : "cancel", node, node.__data__, schedule.index, schedule.group);
		delete schedules[i];
	}
	if (empty) delete node.__transition;
}
//#endregion
//#region node_modules/d3-transition/src/selection/interrupt.js
function interrupt_default(name) {
	return this.each(function() {
		interrupt_default$1(this, name);
	});
}
//#endregion
//#region node_modules/d3-transition/src/transition/tween.js
function tweenRemove(id, name) {
	var tween0, tween1;
	return function() {
		var schedule = set(this, id), tween = schedule.tween;
		if (tween !== tween0) {
			tween1 = tween0 = tween;
			for (var i = 0, n = tween1.length; i < n; ++i) if (tween1[i].name === name) {
				tween1 = tween1.slice();
				tween1.splice(i, 1);
				break;
			}
		}
		schedule.tween = tween1;
	};
}
function tweenFunction(id, name, value) {
	var tween0, tween1;
	if (typeof value !== "function") throw new Error();
	return function() {
		var schedule = set(this, id), tween = schedule.tween;
		if (tween !== tween0) {
			tween1 = (tween0 = tween).slice();
			for (var t = {
				name,
				value
			}, i = 0, n = tween1.length; i < n; ++i) if (tween1[i].name === name) {
				tween1[i] = t;
				break;
			}
			if (i === n) tween1.push(t);
		}
		schedule.tween = tween1;
	};
}
function tween_default(name, value) {
	var id = this._id;
	name += "";
	if (arguments.length < 2) {
		var tween = get(this.node(), id).tween;
		for (var i = 0, n = tween.length, t; i < n; ++i) if ((t = tween[i]).name === name) return t.value;
		return null;
	}
	return this.each((value == null ? tweenRemove : tweenFunction)(id, name, value));
}
function tweenValue(transition, name, value) {
	var id = transition._id;
	transition.each(function() {
		var schedule = set(this, id);
		(schedule.value || (schedule.value = {}))[name] = value.apply(this, arguments);
	});
	return function(node) {
		return get(node, id).value[name];
	};
}
//#endregion
//#region node_modules/d3-transition/src/transition/interpolate.js
function interpolate_default(a, b) {
	var c;
	return (typeof b === "number" ? number_default : b instanceof color ? rgb_default : (c = color(b)) ? (b = c, rgb_default) : string_default)(a, b);
}
//#endregion
//#region node_modules/d3-transition/src/transition/attr.js
function attrRemove(name) {
	return function() {
		this.removeAttribute(name);
	};
}
function attrRemoveNS(fullname) {
	return function() {
		this.removeAttributeNS(fullname.space, fullname.local);
	};
}
function attrConstant(name, interpolate, value1) {
	var string00, string1 = value1 + "", interpolate0;
	return function() {
		var string0 = this.getAttribute(name);
		return string0 === string1 ? null : string0 === string00 ? interpolate0 : interpolate0 = interpolate(string00 = string0, value1);
	};
}
function attrConstantNS(fullname, interpolate, value1) {
	var string00, string1 = value1 + "", interpolate0;
	return function() {
		var string0 = this.getAttributeNS(fullname.space, fullname.local);
		return string0 === string1 ? null : string0 === string00 ? interpolate0 : interpolate0 = interpolate(string00 = string0, value1);
	};
}
function attrFunction(name, interpolate, value) {
	var string00, string10, interpolate0;
	return function() {
		var string0, value1 = value(this), string1;
		if (value1 == null) return void this.removeAttribute(name);
		string0 = this.getAttribute(name);
		string1 = value1 + "";
		return string0 === string1 ? null : string0 === string00 && string1 === string10 ? interpolate0 : (string10 = string1, interpolate0 = interpolate(string00 = string0, value1));
	};
}
function attrFunctionNS(fullname, interpolate, value) {
	var string00, string10, interpolate0;
	return function() {
		var string0, value1 = value(this), string1;
		if (value1 == null) return void this.removeAttributeNS(fullname.space, fullname.local);
		string0 = this.getAttributeNS(fullname.space, fullname.local);
		string1 = value1 + "";
		return string0 === string1 ? null : string0 === string00 && string1 === string10 ? interpolate0 : (string10 = string1, interpolate0 = interpolate(string00 = string0, value1));
	};
}
function attr_default(name, value) {
	var fullname = namespace_default(name), i = fullname === "transform" ? interpolateTransformSvg : interpolate_default;
	return this.attrTween(name, typeof value === "function" ? (fullname.local ? attrFunctionNS : attrFunction)(fullname, i, tweenValue(this, "attr." + name, value)) : value == null ? (fullname.local ? attrRemoveNS : attrRemove)(fullname) : (fullname.local ? attrConstantNS : attrConstant)(fullname, i, value));
}
//#endregion
//#region node_modules/d3-transition/src/transition/attrTween.js
function attrInterpolate(name, i) {
	return function(t) {
		this.setAttribute(name, i.call(this, t));
	};
}
function attrInterpolateNS(fullname, i) {
	return function(t) {
		this.setAttributeNS(fullname.space, fullname.local, i.call(this, t));
	};
}
function attrTweenNS(fullname, value) {
	var t0, i0;
	function tween() {
		var i = value.apply(this, arguments);
		if (i !== i0) t0 = (i0 = i) && attrInterpolateNS(fullname, i);
		return t0;
	}
	tween._value = value;
	return tween;
}
function attrTween(name, value) {
	var t0, i0;
	function tween() {
		var i = value.apply(this, arguments);
		if (i !== i0) t0 = (i0 = i) && attrInterpolate(name, i);
		return t0;
	}
	tween._value = value;
	return tween;
}
function attrTween_default(name, value) {
	var key = "attr." + name;
	if (arguments.length < 2) return (key = this.tween(key)) && key._value;
	if (value == null) return this.tween(key, null);
	if (typeof value !== "function") throw new Error();
	var fullname = namespace_default(name);
	return this.tween(key, (fullname.local ? attrTweenNS : attrTween)(fullname, value));
}
//#endregion
//#region node_modules/d3-transition/src/transition/delay.js
function delayFunction(id, value) {
	return function() {
		init(this, id).delay = +value.apply(this, arguments);
	};
}
function delayConstant(id, value) {
	return value = +value, function() {
		init(this, id).delay = value;
	};
}
function delay_default(value) {
	var id = this._id;
	return arguments.length ? this.each((typeof value === "function" ? delayFunction : delayConstant)(id, value)) : get(this.node(), id).delay;
}
//#endregion
//#region node_modules/d3-transition/src/transition/duration.js
function durationFunction(id, value) {
	return function() {
		set(this, id).duration = +value.apply(this, arguments);
	};
}
function durationConstant(id, value) {
	return value = +value, function() {
		set(this, id).duration = value;
	};
}
function duration_default(value) {
	var id = this._id;
	return arguments.length ? this.each((typeof value === "function" ? durationFunction : durationConstant)(id, value)) : get(this.node(), id).duration;
}
//#endregion
//#region node_modules/d3-transition/src/transition/ease.js
function easeConstant(id, value) {
	if (typeof value !== "function") throw new Error();
	return function() {
		set(this, id).ease = value;
	};
}
function ease_default(value) {
	var id = this._id;
	return arguments.length ? this.each(easeConstant(id, value)) : get(this.node(), id).ease;
}
//#endregion
//#region node_modules/d3-transition/src/transition/easeVarying.js
function easeVarying(id, value) {
	return function() {
		var v = value.apply(this, arguments);
		if (typeof v !== "function") throw new Error();
		set(this, id).ease = v;
	};
}
function easeVarying_default(value) {
	if (typeof value !== "function") throw new Error();
	return this.each(easeVarying(this._id, value));
}
//#endregion
//#region node_modules/d3-transition/src/transition/filter.js
function filter_default(match) {
	if (typeof match !== "function") match = matcher_default(match);
	for (var groups = this._groups, m = groups.length, subgroups = new Array(m), j = 0; j < m; ++j) for (var group = groups[j], n = group.length, subgroup = subgroups[j] = [], node, i = 0; i < n; ++i) if ((node = group[i]) && match.call(node, node.__data__, i, group)) subgroup.push(node);
	return new Transition(subgroups, this._parents, this._name, this._id);
}
//#endregion
//#region node_modules/d3-transition/src/transition/merge.js
function merge_default(transition) {
	if (transition._id !== this._id) throw new Error();
	for (var groups0 = this._groups, groups1 = transition._groups, m0 = groups0.length, m1 = groups1.length, m = Math.min(m0, m1), merges = new Array(m0), j = 0; j < m; ++j) for (var group0 = groups0[j], group1 = groups1[j], n = group0.length, merge = merges[j] = new Array(n), node, i = 0; i < n; ++i) if (node = group0[i] || group1[i]) merge[i] = node;
	for (; j < m0; ++j) merges[j] = groups0[j];
	return new Transition(merges, this._parents, this._name, this._id);
}
//#endregion
//#region node_modules/d3-transition/src/transition/on.js
function start(name) {
	return (name + "").trim().split(/^|\s+/).every(function(t) {
		var i = t.indexOf(".");
		if (i >= 0) t = t.slice(0, i);
		return !t || t === "start";
	});
}
function onFunction(id, name, listener) {
	var on0, on1, sit = start(name) ? init : set;
	return function() {
		var schedule = sit(this, id), on = schedule.on;
		if (on !== on0) (on1 = (on0 = on).copy()).on(name, listener);
		schedule.on = on1;
	};
}
function on_default(name, listener) {
	var id = this._id;
	return arguments.length < 2 ? get(this.node(), id).on.on(name) : this.each(onFunction(id, name, listener));
}
//#endregion
//#region node_modules/d3-transition/src/transition/remove.js
function removeFunction(id) {
	return function() {
		var parent = this.parentNode;
		for (var i in this.__transition) if (+i !== id) return;
		if (parent) parent.removeChild(this);
	};
}
function remove_default() {
	return this.on("end.remove", removeFunction(this._id));
}
//#endregion
//#region node_modules/d3-transition/src/transition/select.js
function select_default(select) {
	var name = this._name, id = this._id;
	if (typeof select !== "function") select = selector_default(select);
	for (var groups = this._groups, m = groups.length, subgroups = new Array(m), j = 0; j < m; ++j) for (var group = groups[j], n = group.length, subgroup = subgroups[j] = new Array(n), node, subnode, i = 0; i < n; ++i) if ((node = group[i]) && (subnode = select.call(node, node.__data__, i, group))) {
		if ("__data__" in node) subnode.__data__ = node.__data__;
		subgroup[i] = subnode;
		schedule_default(subgroup[i], name, id, i, subgroup, get(node, id));
	}
	return new Transition(subgroups, this._parents, name, id);
}
//#endregion
//#region node_modules/d3-transition/src/transition/selectAll.js
function selectAll_default(select) {
	var name = this._name, id = this._id;
	if (typeof select !== "function") select = selectorAll_default(select);
	for (var groups = this._groups, m = groups.length, subgroups = [], parents = [], j = 0; j < m; ++j) for (var group = groups[j], n = group.length, node, i = 0; i < n; ++i) if (node = group[i]) {
		for (var children = select.call(node, node.__data__, i, group), child, inherit = get(node, id), k = 0, l = children.length; k < l; ++k) if (child = children[k]) schedule_default(child, name, id, k, children, inherit);
		subgroups.push(children);
		parents.push(node);
	}
	return new Transition(subgroups, parents, name, id);
}
//#endregion
//#region node_modules/d3-transition/src/transition/selection.js
var Selection = selection.prototype.constructor;
function selection_default() {
	return new Selection(this._groups, this._parents);
}
//#endregion
//#region node_modules/d3-transition/src/transition/style.js
function styleNull(name, interpolate) {
	var string00, string10, interpolate0;
	return function() {
		var string0 = styleValue(this, name), string1 = (this.style.removeProperty(name), styleValue(this, name));
		return string0 === string1 ? null : string0 === string00 && string1 === string10 ? interpolate0 : interpolate0 = interpolate(string00 = string0, string10 = string1);
	};
}
function styleRemove(name) {
	return function() {
		this.style.removeProperty(name);
	};
}
function styleConstant(name, interpolate, value1) {
	var string00, string1 = value1 + "", interpolate0;
	return function() {
		var string0 = styleValue(this, name);
		return string0 === string1 ? null : string0 === string00 ? interpolate0 : interpolate0 = interpolate(string00 = string0, value1);
	};
}
function styleFunction(name, interpolate, value) {
	var string00, string10, interpolate0;
	return function() {
		var string0 = styleValue(this, name), value1 = value(this), string1 = value1 + "";
		if (value1 == null) string1 = value1 = (this.style.removeProperty(name), styleValue(this, name));
		return string0 === string1 ? null : string0 === string00 && string1 === string10 ? interpolate0 : (string10 = string1, interpolate0 = interpolate(string00 = string0, value1));
	};
}
function styleMaybeRemove(id, name) {
	var on0, on1, listener0, key = "style." + name, event = "end." + key, remove;
	return function() {
		var schedule = set(this, id), on = schedule.on, listener = schedule.value[key] == null ? remove || (remove = styleRemove(name)) : void 0;
		if (on !== on0 || listener0 !== listener) (on1 = (on0 = on).copy()).on(event, listener0 = listener);
		schedule.on = on1;
	};
}
function style_default(name, value, priority) {
	var i = (name += "") === "transform" ? interpolateTransformCss : interpolate_default;
	return value == null ? this.styleTween(name, styleNull(name, i)).on("end.style." + name, styleRemove(name)) : typeof value === "function" ? this.styleTween(name, styleFunction(name, i, tweenValue(this, "style." + name, value))).each(styleMaybeRemove(this._id, name)) : this.styleTween(name, styleConstant(name, i, value), priority).on("end.style." + name, null);
}
//#endregion
//#region node_modules/d3-transition/src/transition/styleTween.js
function styleInterpolate(name, i, priority) {
	return function(t) {
		this.style.setProperty(name, i.call(this, t), priority);
	};
}
function styleTween(name, value, priority) {
	var t, i0;
	function tween() {
		var i = value.apply(this, arguments);
		if (i !== i0) t = (i0 = i) && styleInterpolate(name, i, priority);
		return t;
	}
	tween._value = value;
	return tween;
}
function styleTween_default(name, value, priority) {
	var key = "style." + (name += "");
	if (arguments.length < 2) return (key = this.tween(key)) && key._value;
	if (value == null) return this.tween(key, null);
	if (typeof value !== "function") throw new Error();
	return this.tween(key, styleTween(name, value, priority == null ? "" : priority));
}
//#endregion
//#region node_modules/d3-transition/src/transition/text.js
function textConstant(value) {
	return function() {
		this.textContent = value;
	};
}
function textFunction(value) {
	return function() {
		var value1 = value(this);
		this.textContent = value1 == null ? "" : value1;
	};
}
function text_default(value) {
	return this.tween("text", typeof value === "function" ? textFunction(tweenValue(this, "text", value)) : textConstant(value == null ? "" : value + ""));
}
//#endregion
//#region node_modules/d3-transition/src/transition/textTween.js
function textInterpolate(i) {
	return function(t) {
		this.textContent = i.call(this, t);
	};
}
function textTween(value) {
	var t0, i0;
	function tween() {
		var i = value.apply(this, arguments);
		if (i !== i0) t0 = (i0 = i) && textInterpolate(i);
		return t0;
	}
	tween._value = value;
	return tween;
}
function textTween_default(value) {
	var key = "text";
	if (arguments.length < 1) return (key = this.tween(key)) && key._value;
	if (value == null) return this.tween(key, null);
	if (typeof value !== "function") throw new Error();
	return this.tween(key, textTween(value));
}
//#endregion
//#region node_modules/d3-transition/src/transition/transition.js
function transition_default$1() {
	var name = this._name, id0 = this._id, id1 = newId();
	for (var groups = this._groups, m = groups.length, j = 0; j < m; ++j) for (var group = groups[j], n = group.length, node, i = 0; i < n; ++i) if (node = group[i]) {
		var inherit = get(node, id0);
		schedule_default(node, name, id1, i, group, {
			time: inherit.time + inherit.delay + inherit.duration,
			delay: 0,
			duration: inherit.duration,
			ease: inherit.ease
		});
	}
	return new Transition(groups, this._parents, name, id1);
}
//#endregion
//#region node_modules/d3-transition/src/transition/end.js
function end_default() {
	var on0, on1, that = this, id = that._id, size = that.size();
	return new Promise(function(resolve, reject) {
		var cancel = { value: reject }, end = { value: function() {
			if (--size === 0) resolve();
		} };
		that.each(function() {
			var schedule = set(this, id), on = schedule.on;
			if (on !== on0) {
				on1 = (on0 = on).copy();
				on1._.cancel.push(cancel);
				on1._.interrupt.push(cancel);
				on1._.end.push(end);
			}
			schedule.on = on1;
		});
		if (size === 0) resolve();
	});
}
//#endregion
//#region node_modules/d3-transition/src/transition/index.js
var id = 0;
function Transition(groups, parents, name, id) {
	this._groups = groups;
	this._parents = parents;
	this._name = name;
	this._id = id;
}
function transition(name) {
	return selection().transition(name);
}
function newId() {
	return ++id;
}
var selection_prototype = selection.prototype;
Transition.prototype = transition.prototype = {
	constructor: Transition,
	select: select_default,
	selectAll: selectAll_default,
	selectChild: selection_prototype.selectChild,
	selectChildren: selection_prototype.selectChildren,
	filter: filter_default,
	merge: merge_default,
	selection: selection_default,
	transition: transition_default$1,
	call: selection_prototype.call,
	nodes: selection_prototype.nodes,
	node: selection_prototype.node,
	size: selection_prototype.size,
	empty: selection_prototype.empty,
	each: selection_prototype.each,
	on: on_default,
	attr: attr_default,
	attrTween: attrTween_default,
	style: style_default,
	styleTween: styleTween_default,
	text: text_default,
	textTween: textTween_default,
	remove: remove_default,
	tween: tween_default,
	delay: delay_default,
	duration: duration_default,
	ease: ease_default,
	easeVarying: easeVarying_default,
	end: end_default,
	[Symbol.iterator]: selection_prototype[Symbol.iterator]
};
//#endregion
//#region node_modules/d3-ease/src/cubic.js
function cubicInOut(t) {
	return ((t *= 2) <= 1 ? t * t * t : (t -= 2) * t * t + 2) / 2;
}
//#endregion
//#region node_modules/d3-transition/src/selection/transition.js
var defaultTiming = {
	time: null,
	delay: 0,
	duration: 250,
	ease: cubicInOut
};
function inherit(node, id) {
	var timing;
	while (!(timing = node.__transition) || !(timing = timing[id])) if (!(node = node.parentNode)) throw new Error(`transition ${id} not found`);
	return timing;
}
function transition_default(name) {
	var id, timing;
	if (name instanceof Transition) id = name._id, name = name._name;
	else id = newId(), (timing = defaultTiming).time = now(), name = name == null ? null : name + "";
	for (var groups = this._groups, m = groups.length, j = 0; j < m; ++j) for (var group = groups[j], n = group.length, node, i = 0; i < n; ++i) if (node = group[i]) schedule_default(node, name, id, i, group, timing || inherit(node, id));
	return new Transition(groups, this._parents, name, id);
}
//#endregion
//#region node_modules/d3-transition/src/selection/index.js
selection.prototype.interrupt = interrupt_default;
selection.prototype.transition = transition_default;
//#endregion
//#region node_modules/d3-zoom/src/constant.js
var constant_default = (x) => () => x;
//#endregion
//#region node_modules/d3-zoom/src/event.js
function ZoomEvent(type, { sourceEvent, target, transform, dispatch }) {
	Object.defineProperties(this, {
		type: {
			value: type,
			enumerable: true,
			configurable: true
		},
		sourceEvent: {
			value: sourceEvent,
			enumerable: true,
			configurable: true
		},
		target: {
			value: target,
			enumerable: true,
			configurable: true
		},
		transform: {
			value: transform,
			enumerable: true,
			configurable: true
		},
		_: { value: dispatch }
	});
}
//#endregion
//#region node_modules/d3-zoom/src/transform.js
function Transform(k, x, y) {
	this.k = k;
	this.x = x;
	this.y = y;
}
Transform.prototype = {
	constructor: Transform,
	scale: function(k) {
		return k === 1 ? this : new Transform(this.k * k, this.x, this.y);
	},
	translate: function(x, y) {
		return x === 0 & y === 0 ? this : new Transform(this.k, this.x + this.k * x, this.y + this.k * y);
	},
	apply: function(point) {
		return [point[0] * this.k + this.x, point[1] * this.k + this.y];
	},
	applyX: function(x) {
		return x * this.k + this.x;
	},
	applyY: function(y) {
		return y * this.k + this.y;
	},
	invert: function(location) {
		return [(location[0] - this.x) / this.k, (location[1] - this.y) / this.k];
	},
	invertX: function(x) {
		return (x - this.x) / this.k;
	},
	invertY: function(y) {
		return (y - this.y) / this.k;
	},
	rescaleX: function(x) {
		return x.copy().domain(x.range().map(this.invertX, this).map(x.invert, x));
	},
	rescaleY: function(y) {
		return y.copy().domain(y.range().map(this.invertY, this).map(y.invert, y));
	},
	toString: function() {
		return "translate(" + this.x + "," + this.y + ") scale(" + this.k + ")";
	}
};
var identity = new Transform(1, 0, 0);
transform.prototype = Transform.prototype;
function transform(node) {
	while (!node.__zoom) if (!(node = node.parentNode)) return identity;
	return node.__zoom;
}
//#endregion
//#region node_modules/d3-zoom/src/noevent.js
function nopropagation(event) {
	event.stopImmediatePropagation();
}
function noevent_default(event) {
	event.preventDefault();
	event.stopImmediatePropagation();
}
//#endregion
//#region node_modules/d3-zoom/src/zoom.js
function defaultFilter(event) {
	return (!event.ctrlKey || event.type === "wheel") && !event.button;
}
function defaultExtent() {
	var e = this;
	if (e instanceof SVGElement) {
		e = e.ownerSVGElement || e;
		if (e.hasAttribute("viewBox")) {
			e = e.viewBox.baseVal;
			return [[e.x, e.y], [e.x + e.width, e.y + e.height]];
		}
		return [[0, 0], [e.width.baseVal.value, e.height.baseVal.value]];
	}
	return [[0, 0], [e.clientWidth, e.clientHeight]];
}
function defaultTransform() {
	return this.__zoom || identity;
}
function defaultWheelDelta(event) {
	return -event.deltaY * (event.deltaMode === 1 ? .05 : event.deltaMode ? 1 : .002) * (event.ctrlKey ? 10 : 1);
}
function defaultTouchable() {
	return navigator.maxTouchPoints || "ontouchstart" in this;
}
function defaultConstrain(transform, extent, translateExtent) {
	var dx0 = transform.invertX(extent[0][0]) - translateExtent[0][0], dx1 = transform.invertX(extent[1][0]) - translateExtent[1][0], dy0 = transform.invertY(extent[0][1]) - translateExtent[0][1], dy1 = transform.invertY(extent[1][1]) - translateExtent[1][1];
	return transform.translate(dx1 > dx0 ? (dx0 + dx1) / 2 : Math.min(0, dx0) || Math.max(0, dx1), dy1 > dy0 ? (dy0 + dy1) / 2 : Math.min(0, dy0) || Math.max(0, dy1));
}
function zoom_default() {
	var filter = defaultFilter, extent = defaultExtent, constrain = defaultConstrain, wheelDelta = defaultWheelDelta, touchable = defaultTouchable, scaleExtent = [0, Infinity], translateExtent = [[-Infinity, -Infinity], [Infinity, Infinity]], duration = 250, interpolate = zoom_default$1, listeners = dispatch("start", "zoom", "end"), touchstarting, touchfirst, touchending, touchDelay = 500, wheelDelay = 150, clickDistance2 = 0, tapDistance = 10;
	function zoom(selection) {
		selection.property("__zoom", defaultTransform).on("wheel.zoom", wheeled, { passive: false }).on("mousedown.zoom", mousedowned).on("dblclick.zoom", dblclicked).filter(touchable).on("touchstart.zoom", touchstarted).on("touchmove.zoom", touchmoved).on("touchend.zoom touchcancel.zoom", touchended).style("-webkit-tap-highlight-color", "rgba(0,0,0,0)");
	}
	zoom.transform = function(collection, transform, point, event) {
		var selection = collection.selection ? collection.selection() : collection;
		selection.property("__zoom", defaultTransform);
		if (collection !== selection) schedule(collection, transform, point, event);
		else selection.interrupt().each(function() {
			gesture(this, arguments).event(event).start().zoom(null, typeof transform === "function" ? transform.apply(this, arguments) : transform).end();
		});
	};
	zoom.scaleBy = function(selection, k, p, event) {
		zoom.scaleTo(selection, function() {
			return this.__zoom.k * (typeof k === "function" ? k.apply(this, arguments) : k);
		}, p, event);
	};
	zoom.scaleTo = function(selection, k, p, event) {
		zoom.transform(selection, function() {
			var e = extent.apply(this, arguments), t0 = this.__zoom, p0 = p == null ? centroid(e) : typeof p === "function" ? p.apply(this, arguments) : p, p1 = t0.invert(p0), k1 = typeof k === "function" ? k.apply(this, arguments) : k;
			return constrain(translate(scale(t0, k1), p0, p1), e, translateExtent);
		}, p, event);
	};
	zoom.translateBy = function(selection, x, y, event) {
		zoom.transform(selection, function() {
			return constrain(this.__zoom.translate(typeof x === "function" ? x.apply(this, arguments) : x, typeof y === "function" ? y.apply(this, arguments) : y), extent.apply(this, arguments), translateExtent);
		}, null, event);
	};
	zoom.translateTo = function(selection, x, y, p, event) {
		zoom.transform(selection, function() {
			var e = extent.apply(this, arguments), t = this.__zoom, p0 = p == null ? centroid(e) : typeof p === "function" ? p.apply(this, arguments) : p;
			return constrain(identity.translate(p0[0], p0[1]).scale(t.k).translate(typeof x === "function" ? -x.apply(this, arguments) : -x, typeof y === "function" ? -y.apply(this, arguments) : -y), e, translateExtent);
		}, p, event);
	};
	function scale(transform, k) {
		k = Math.max(scaleExtent[0], Math.min(scaleExtent[1], k));
		return k === transform.k ? transform : new Transform(k, transform.x, transform.y);
	}
	function translate(transform, p0, p1) {
		var x = p0[0] - p1[0] * transform.k, y = p0[1] - p1[1] * transform.k;
		return x === transform.x && y === transform.y ? transform : new Transform(transform.k, x, y);
	}
	function centroid(extent) {
		return [(+extent[0][0] + +extent[1][0]) / 2, (+extent[0][1] + +extent[1][1]) / 2];
	}
	function schedule(transition, transform, point, event) {
		transition.on("start.zoom", function() {
			gesture(this, arguments).event(event).start();
		}).on("interrupt.zoom end.zoom", function() {
			gesture(this, arguments).event(event).end();
		}).tween("zoom", function() {
			var that = this, args = arguments, g = gesture(that, args).event(event), e = extent.apply(that, args), p = point == null ? centroid(e) : typeof point === "function" ? point.apply(that, args) : point, w = Math.max(e[1][0] - e[0][0], e[1][1] - e[0][1]), a = that.__zoom, b = typeof transform === "function" ? transform.apply(that, args) : transform, i = interpolate(a.invert(p).concat(w / a.k), b.invert(p).concat(w / b.k));
			return function(t) {
				if (t === 1) t = b;
				else {
					var l = i(t), k = w / l[2];
					t = new Transform(k, p[0] - l[0] * k, p[1] - l[1] * k);
				}
				g.zoom(null, t);
			};
		});
	}
	function gesture(that, args, clean) {
		return !clean && that.__zooming || new Gesture(that, args);
	}
	function Gesture(that, args) {
		this.that = that;
		this.args = args;
		this.active = 0;
		this.sourceEvent = null;
		this.extent = extent.apply(that, args);
		this.taps = 0;
	}
	Gesture.prototype = {
		event: function(event) {
			if (event) this.sourceEvent = event;
			return this;
		},
		start: function() {
			if (++this.active === 1) {
				this.that.__zooming = this;
				this.emit("start");
			}
			return this;
		},
		zoom: function(key, transform) {
			if (this.mouse && key !== "mouse") this.mouse[1] = transform.invert(this.mouse[0]);
			if (this.touch0 && key !== "touch") this.touch0[1] = transform.invert(this.touch0[0]);
			if (this.touch1 && key !== "touch") this.touch1[1] = transform.invert(this.touch1[0]);
			this.that.__zoom = transform;
			this.emit("zoom");
			return this;
		},
		end: function() {
			if (--this.active === 0) {
				delete this.that.__zooming;
				this.emit("end");
			}
			return this;
		},
		emit: function(type) {
			var d = select_default$1(this.that).datum();
			listeners.call(type, this.that, new ZoomEvent(type, {
				sourceEvent: this.sourceEvent,
				target: zoom,
				type,
				transform: this.that.__zoom,
				dispatch: listeners
			}), d);
		}
	};
	function wheeled(event, ...args) {
		if (!filter.apply(this, arguments)) return;
		var g = gesture(this, args).event(event), t = this.__zoom, k = Math.max(scaleExtent[0], Math.min(scaleExtent[1], t.k * Math.pow(2, wheelDelta.apply(this, arguments)))), p = pointer_default(event);
		if (g.wheel) {
			if (g.mouse[0][0] !== p[0] || g.mouse[0][1] !== p[1]) g.mouse[1] = t.invert(g.mouse[0] = p);
			clearTimeout(g.wheel);
		} else if (t.k === k) return;
		else {
			g.mouse = [p, t.invert(p)];
			interrupt_default$1(this);
			g.start();
		}
		noevent_default(event);
		g.wheel = setTimeout(wheelidled, wheelDelay);
		g.zoom("mouse", constrain(translate(scale(t, k), g.mouse[0], g.mouse[1]), g.extent, translateExtent));
		function wheelidled() {
			g.wheel = null;
			g.end();
		}
	}
	function mousedowned(event, ...args) {
		if (touchending || !filter.apply(this, arguments)) return;
		var currentTarget = event.currentTarget, g = gesture(this, args, true).event(event), v = select_default$1(event.view).on("mousemove.zoom", mousemoved, true).on("mouseup.zoom", mouseupped, true), p = pointer_default(event, currentTarget), x0 = event.clientX, y0 = event.clientY;
		nodrag_default(event.view);
		nopropagation(event);
		g.mouse = [p, this.__zoom.invert(p)];
		interrupt_default$1(this);
		g.start();
		function mousemoved(event) {
			noevent_default(event);
			if (!g.moved) {
				var dx = event.clientX - x0, dy = event.clientY - y0;
				g.moved = dx * dx + dy * dy > clickDistance2;
			}
			g.event(event).zoom("mouse", constrain(translate(g.that.__zoom, g.mouse[0] = pointer_default(event, currentTarget), g.mouse[1]), g.extent, translateExtent));
		}
		function mouseupped(event) {
			v.on("mousemove.zoom mouseup.zoom", null);
			yesdrag(event.view, g.moved);
			noevent_default(event);
			g.event(event).end();
		}
	}
	function dblclicked(event, ...args) {
		if (!filter.apply(this, arguments)) return;
		var t0 = this.__zoom, p0 = pointer_default(event.changedTouches ? event.changedTouches[0] : event, this), p1 = t0.invert(p0), k1 = t0.k * (event.shiftKey ? .5 : 2), t1 = constrain(translate(scale(t0, k1), p0, p1), extent.apply(this, args), translateExtent);
		noevent_default(event);
		if (duration > 0) select_default$1(this).transition().duration(duration).call(schedule, t1, p0, event);
		else select_default$1(this).call(zoom.transform, t1, p0, event);
	}
	function touchstarted(event, ...args) {
		if (!filter.apply(this, arguments)) return;
		var touches = event.touches, n = touches.length, g = gesture(this, args, event.changedTouches.length === n).event(event), started, i, t, p;
		nopropagation(event);
		for (i = 0; i < n; ++i) {
			t = touches[i], p = pointer_default(t, this);
			p = [
				p,
				this.__zoom.invert(p),
				t.identifier
			];
			if (!g.touch0) g.touch0 = p, started = true, g.taps = 1 + !!touchstarting;
			else if (!g.touch1 && g.touch0[2] !== p[2]) g.touch1 = p, g.taps = 0;
		}
		if (touchstarting) touchstarting = clearTimeout(touchstarting);
		if (started) {
			if (g.taps < 2) touchfirst = p[0], touchstarting = setTimeout(function() {
				touchstarting = null;
			}, touchDelay);
			interrupt_default$1(this);
			g.start();
		}
	}
	function touchmoved(event, ...args) {
		if (!this.__zooming) return;
		var g = gesture(this, args).event(event), touches = event.changedTouches, n = touches.length, i, t, p, l;
		noevent_default(event);
		for (i = 0; i < n; ++i) {
			t = touches[i], p = pointer_default(t, this);
			if (g.touch0 && g.touch0[2] === t.identifier) g.touch0[0] = p;
			else if (g.touch1 && g.touch1[2] === t.identifier) g.touch1[0] = p;
		}
		t = g.that.__zoom;
		if (g.touch1) {
			var p0 = g.touch0[0], l0 = g.touch0[1], p1 = g.touch1[0], l1 = g.touch1[1], dp = (dp = p1[0] - p0[0]) * dp + (dp = p1[1] - p0[1]) * dp, dl = (dl = l1[0] - l0[0]) * dl + (dl = l1[1] - l0[1]) * dl;
			t = scale(t, Math.sqrt(dp / dl));
			p = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2];
			l = [(l0[0] + l1[0]) / 2, (l0[1] + l1[1]) / 2];
		} else if (g.touch0) p = g.touch0[0], l = g.touch0[1];
		else return;
		g.zoom("touch", constrain(translate(t, p, l), g.extent, translateExtent));
	}
	function touchended(event, ...args) {
		if (!this.__zooming) return;
		var g = gesture(this, args).event(event), touches = event.changedTouches, n = touches.length, i, t;
		nopropagation(event);
		if (touchending) clearTimeout(touchending);
		touchending = setTimeout(function() {
			touchending = null;
		}, touchDelay);
		for (i = 0; i < n; ++i) {
			t = touches[i];
			if (g.touch0 && g.touch0[2] === t.identifier) delete g.touch0;
			else if (g.touch1 && g.touch1[2] === t.identifier) delete g.touch1;
		}
		if (g.touch1 && !g.touch0) g.touch0 = g.touch1, delete g.touch1;
		if (g.touch0) g.touch0[1] = this.__zoom.invert(g.touch0[0]);
		else {
			g.end();
			if (g.taps === 2) {
				t = pointer_default(t, this);
				if (Math.hypot(touchfirst[0] - t[0], touchfirst[1] - t[1]) < tapDistance) {
					var p = select_default$1(this).on("dblclick.zoom");
					if (p) p.apply(this, arguments);
				}
			}
		}
	}
	zoom.wheelDelta = function(_) {
		return arguments.length ? (wheelDelta = typeof _ === "function" ? _ : constant_default(+_), zoom) : wheelDelta;
	};
	zoom.filter = function(_) {
		return arguments.length ? (filter = typeof _ === "function" ? _ : constant_default(!!_), zoom) : filter;
	};
	zoom.touchable = function(_) {
		return arguments.length ? (touchable = typeof _ === "function" ? _ : constant_default(!!_), zoom) : touchable;
	};
	zoom.extent = function(_) {
		return arguments.length ? (extent = typeof _ === "function" ? _ : constant_default([[+_[0][0], +_[0][1]], [+_[1][0], +_[1][1]]]), zoom) : extent;
	};
	zoom.scaleExtent = function(_) {
		return arguments.length ? (scaleExtent[0] = +_[0], scaleExtent[1] = +_[1], zoom) : [scaleExtent[0], scaleExtent[1]];
	};
	zoom.translateExtent = function(_) {
		return arguments.length ? (translateExtent[0][0] = +_[0][0], translateExtent[1][0] = +_[1][0], translateExtent[0][1] = +_[0][1], translateExtent[1][1] = +_[1][1], zoom) : [[translateExtent[0][0], translateExtent[0][1]], [translateExtent[1][0], translateExtent[1][1]]];
	};
	zoom.constrain = function(_) {
		return arguments.length ? (constrain = _, zoom) : constrain;
	};
	zoom.duration = function(_) {
		return arguments.length ? (duration = +_, zoom) : duration;
	};
	zoom.interpolate = function(_) {
		return arguments.length ? (interpolate = _, zoom) : interpolate;
	};
	zoom.on = function() {
		var value = listeners.on.apply(listeners, arguments);
		return value === listeners ? zoom : value;
	};
	zoom.clickDistance = function(_) {
		return arguments.length ? (clickDistance2 = (_ = +_) * _, zoom) : Math.sqrt(clickDistance2);
	};
	zoom.tapDistance = function(_) {
		return arguments.length ? (tapDistance = +_, zoom) : tapDistance;
	};
	return zoom;
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/index-a12c80bd.js
function _defineProperty(obj, key, value) {
	if (key in obj) Object.defineProperty(obj, key, {
		value,
		enumerable: true,
		configurable: true,
		writable: true
	});
	else obj[key] = value;
	return obj;
}
function _arrayLikeToArray(arr, len) {
	if (len == null || len > arr.length) len = arr.length;
	for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i];
	return arr2;
}
function _unsupportedIterableToArray(o, minLen) {
	if (!o) return;
	if (typeof o === "string") return _arrayLikeToArray(o, minLen);
	var n = Object.prototype.toString.call(o).slice(8, -1);
	if (n === "Object" && o.constructor) n = o.constructor.name;
	if (n === "Map" || n === "Set") return Array.from(o);
	if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen);
}
function _arrayWithHoles(arr) {
	if (Array.isArray(arr)) return arr;
}
function _iterableToArrayLimit(arr, i) {
	var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"];
	if (_i == null) return;
	var _arr = [];
	var _n = true;
	var _d = false;
	var _s, _e;
	try {
		for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) {
			_arr.push(_s.value);
			if (i && _arr.length === i) break;
		}
	} catch (err) {
		_d = true;
		_e = err;
	} finally {
		try {
			if (!_n && _i["return"] != null) _i["return"]();
		} finally {
			if (_d) throw _e;
		}
	}
	return _arr;
}
function _nonIterableRest() {
	throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function _slicedToArray(arr, i) {
	return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest();
}
var ConnectionMode;
(function(ConnectionMode) {
	ConnectionMode["Strict"] = "strict";
	ConnectionMode["Loose"] = "loose";
})(ConnectionMode || (ConnectionMode = {}));
var BackgroundVariant;
(function(BackgroundVariant) {
	BackgroundVariant["Lines"] = "lines";
	BackgroundVariant["Dots"] = "dots";
})(BackgroundVariant || (BackgroundVariant = {}));
var PanOnScrollMode;
(function(PanOnScrollMode) {
	PanOnScrollMode["Free"] = "free";
	PanOnScrollMode["Vertical"] = "vertical";
	PanOnScrollMode["Horizontal"] = "horizontal";
})(PanOnScrollMode || (PanOnScrollMode = {}));
var ConnectionLineType;
(function(ConnectionLineType) {
	ConnectionLineType["Bezier"] = "default";
	ConnectionLineType["Straight"] = "straight";
	ConnectionLineType["Step"] = "step";
	ConnectionLineType["SmoothStep"] = "smoothstep";
	ConnectionLineType["SimpleBezier"] = "simplebezier";
})(ConnectionLineType || (ConnectionLineType = {}));
var MarkerType;
(function(MarkerType) {
	MarkerType["Arrow"] = "arrow";
	MarkerType["ArrowClosed"] = "arrowclosed";
})(MarkerType || (MarkerType = {}));
var Position;
(function(Position) {
	Position["Left"] = "left";
	Position["Top"] = "top";
	Position["Right"] = "right";
	Position["Bottom"] = "bottom";
})(Position || (Position = {}));
var getDimensions = function getDimensions(node) {
	return {
		width: node.offsetWidth,
		height: node.offsetHeight
	};
};
var clamp = function clamp(val) {
	var min = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0;
	var max = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : 1;
	return Math.min(Math.max(val, min), max);
};
var clampPosition = function clampPosition(position, extent) {
	return {
		x: clamp(position.x, extent[0][0], extent[1][0]),
		y: clamp(position.y, extent[0][1], extent[1][1])
	};
};
var getHostForElement = function getHostForElement(element) {
	var _element$getRootNode, _window;
	return ((_element$getRootNode = element.getRootNode) === null || _element$getRootNode === void 0 ? void 0 : _element$getRootNode.call(element)) || ((_window = window) === null || _window === void 0 ? void 0 : _window.document);
};
var getBoundsOfBoxes = function getBoundsOfBoxes(box1, box2) {
	return {
		x: Math.min(box1.x, box2.x),
		y: Math.min(box1.y, box2.y),
		x2: Math.max(box1.x2, box2.x2),
		y2: Math.max(box1.y2, box2.y2)
	};
};
var rectToBox = function rectToBox(_ref) {
	var x = _ref.x, y = _ref.y, width = _ref.width, height = _ref.height;
	return {
		x,
		y,
		x2: x + width,
		y2: y + height
	};
};
var boxToRect = function boxToRect(_ref2) {
	var x = _ref2.x, y = _ref2.y, x2 = _ref2.x2, y2 = _ref2.y2;
	return {
		x,
		y,
		width: x2 - x,
		height: y2 - y
	};
};
var getBoundsofRects = function getBoundsofRects(rect1, rect2) {
	return boxToRect(getBoundsOfBoxes(rectToBox(rect1), rectToBox(rect2)));
};
var isNumeric = function isNumeric(n) {
	return !isNaN(n) && isFinite(n);
};
var internalsSymbol = Symbol("internals");
function ownKeys$4$4(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$4$4(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$4$4(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$4$4(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function handleParentExpand(res, updateItem) {
	var parent = res.find(function(e) {
		return e.id === updateItem.parentNode;
	});
	if (parent) {
		var extendWidth = updateItem.position.x + updateItem.width - parent.width;
		var extendHeight = updateItem.position.y + updateItem.height - parent.height;
		if (extendWidth > 0 || extendHeight > 0 || updateItem.position.x < 0 || updateItem.position.y < 0) {
			var _parent$style$width, _parent$style$height;
			parent.style = _objectSpread$4$4({}, parent.style) || {};
			parent.style.width = (_parent$style$width = parent.style.width) !== null && _parent$style$width !== void 0 ? _parent$style$width : parent.width;
			parent.style.height = (_parent$style$height = parent.style.height) !== null && _parent$style$height !== void 0 ? _parent$style$height : parent.height;
			if (extendWidth > 0) parent.style.width += extendWidth;
			if (extendHeight > 0) parent.style.height += extendHeight;
			if (updateItem.position.x < 0) {
				var xDiff = Math.abs(updateItem.position.x);
				parent.position.x = parent.position.x - xDiff;
				parent.style.width += xDiff;
				updateItem.position.x = 0;
			}
			if (updateItem.position.y < 0) {
				var yDiff = Math.abs(updateItem.position.y);
				parent.position.y = parent.position.y - yDiff;
				parent.style.height += yDiff;
				updateItem.position.y = 0;
			}
			parent.width = parent.style.width;
			parent.height = parent.style.height;
		}
	}
}
function applyChanges(changes, elements) {
	if (changes.some(function(c) {
		return c.type === "reset";
	})) return changes.filter(function(c) {
		return c.type === "reset";
	}).map(function(c) {
		return c.item;
	});
	var initElements = changes.filter(function(c) {
		return c.type === "add";
	}).map(function(c) {
		return c.item;
	});
	return elements.reduce(function(res, item) {
		var currentChange = changes.find(function(c) {
			return c.id === item.id;
		});
		if (currentChange) switch (currentChange.type) {
			case "select":
				res.push(_objectSpread$4$4(_objectSpread$4$4({}, item), {}, { selected: currentChange.selected }));
				return res;
			case "position":
				var updateItem = _objectSpread$4$4({}, item);
				if (typeof currentChange.position !== "undefined") updateItem.position = currentChange.position;
				if (typeof currentChange.positionAbsolute !== "undefined") updateItem.positionAbsolute = currentChange.positionAbsolute;
				if (typeof currentChange.dragging !== "undefined") updateItem.dragging = currentChange.dragging;
				if (updateItem.expandParent) handleParentExpand(res, updateItem);
				res.push(updateItem);
				return res;
			case "dimensions":
				var _updateItem = _objectSpread$4$4({}, item);
				if (typeof currentChange.dimensions !== "undefined") {
					_updateItem.width = currentChange.dimensions.width;
					_updateItem.height = currentChange.dimensions.height;
				}
				if (_updateItem.expandParent) handleParentExpand(res, _updateItem);
				res.push(_updateItem);
				return res;
			case "remove": return res;
		}
		res.push(item);
		return res;
	}, initElements);
}
function applyNodeChanges(changes, nodes) {
	return applyChanges(changes, nodes);
}
function applyEdgeChanges(changes, edges) {
	return applyChanges(changes, edges);
}
var createSelectionChange = function createSelectionChange(id, selected) {
	return {
		id,
		type: "select",
		selected
	};
};
function getSelectionChanges(items, selectedIds) {
	return items.reduce(function(res, item) {
		var willBeSelected = selectedIds.includes(item.id);
		if (!item.selected && willBeSelected) {
			item.selected = true;
			res.push(createSelectionChange(item.id, true));
		} else if (item.selected && !willBeSelected) {
			item.selected = false;
			res.push(createSelectionChange(item.id, false));
		}
		return res;
	}, []);
}
function ownKeys$3$11(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$3$11(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$3$11(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$3$11(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var getHandleBounds = function getHandleBounds(selector, nodeElement, zoom) {
	var handles = nodeElement.querySelectorAll(selector);
	if (!handles || !handles.length) return null;
	var handlesArray = Array.from(handles);
	var nodeBounds = nodeElement.getBoundingClientRect();
	return handlesArray.map(function(handle) {
		var handleBounds = handle.getBoundingClientRect();
		return _objectSpread$3$11({
			id: handle.getAttribute("data-handleid"),
			position: handle.getAttribute("data-handlepos"),
			x: (handleBounds.left - nodeBounds.left) / zoom,
			y: (handleBounds.top - nodeBounds.top) / zoom
		}, getDimensions(handle));
	});
};
function getMouseHandler$1(id, getState, handler) {
	return handler === void 0 ? handler : function(event) {
		handler(event, _objectSpread$3$11({}, getState().nodeInternals.get(id)));
	};
}
function handleNodeClick(_ref) {
	var id = _ref.id, store = _ref.store;
	var _store$getState = store.getState(), addSelectedNodes = _store$getState.addSelectedNodes, unselectNodesAndEdges = _store$getState.unselectNodesAndEdges, multiSelectionActive = _store$getState.multiSelectionActive;
	var node = _store$getState.nodeInternals.get(id);
	store.setState({ nodesSelectionActive: false });
	if (!node.selected) addSelectedNodes([id]);
	else if (node.selected && multiSelectionActive) unselectNodesAndEdges({ nodes: [node] });
}
function ownKeys$2$12(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$2$12(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$2$12(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$2$12(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var isEdge = function isEdge(element) {
	return "id" in element && "source" in element && "target" in element;
};
var isNode = function isNode(element) {
	return "id" in element && !("source" in element) && !("target" in element);
};
var getOutgoers = function getOutgoers(node, nodes, edges) {
	if (!isNode(node)) return [];
	var outgoerIds = edges.filter(function(e) {
		return e.source === node.id;
	}).map(function(e) {
		return e.target;
	});
	return nodes.filter(function(n) {
		return outgoerIds.includes(n.id);
	});
};
var getIncomers = function getIncomers(node, nodes, edges) {
	if (!isNode(node)) return [];
	var incomersIds = edges.filter(function(e) {
		return e.target === node.id;
	}).map(function(e) {
		return e.source;
	});
	return nodes.filter(function(n) {
		return incomersIds.includes(n.id);
	});
};
var getEdgeId = function getEdgeId(_ref) {
	var source = _ref.source, sourceHandle = _ref.sourceHandle, target = _ref.target, targetHandle = _ref.targetHandle;
	return "reactflow__edge-".concat(source).concat(sourceHandle || "", "-").concat(target).concat(targetHandle || "");
};
var getMarkerId = function getMarkerId(marker, rfId) {
	if (typeof marker === "undefined") return "";
	if (typeof marker === "string") return marker;
	var idPrefix = rfId ? "".concat(rfId, "__") : "";
	return "".concat(idPrefix).concat(Object.keys(marker).sort().map(function(key) {
		return "".concat(key, "=").concat(marker[key]);
	}).join("&"));
};
var connectionExists = function connectionExists(edge, edges) {
	return edges.some(function(el) {
		return el.source === edge.source && el.target === edge.target && (el.sourceHandle === edge.sourceHandle || !el.sourceHandle && !edge.sourceHandle) && (el.targetHandle === edge.targetHandle || !el.targetHandle && !edge.targetHandle);
	});
};
var addEdge = function addEdge(edgeParams, edges) {
	if (!edgeParams.source || !edgeParams.target) {
		console.warn("[React Flow]: Can't create edge. An edge needs a source and a target. Help: https://reactflow.dev/error#600");
		return edges;
	}
	var edge;
	if (isEdge(edgeParams)) edge = _objectSpread$2$12({}, edgeParams);
	else edge = _objectSpread$2$12(_objectSpread$2$12({}, edgeParams), {}, { id: getEdgeId(edgeParams) });
	if (connectionExists(edge, edges)) return edges;
	return edges.concat(edge);
};
var updateEdge = function updateEdge(oldEdge, newConnection, edges) {
	if (!newConnection.source || !newConnection.target) {
		console.warn("[React Flow]: Can't create a new edge. An edge needs a source and a target. Help: https://reactflow.dev/error#600");
		return edges;
	}
	if (!edges.find(function(e) {
		return e.id === oldEdge.id;
	})) {
		console.warn("[React Flow]: The old edge with id=".concat(oldEdge.id, " does not exist. Help: https://reactflow.dev/error#700"));
		return edges;
	}
	var edge = _objectSpread$2$12(_objectSpread$2$12({}, oldEdge), {}, {
		id: getEdgeId(newConnection),
		source: newConnection.source,
		target: newConnection.target,
		sourceHandle: newConnection.sourceHandle,
		targetHandle: newConnection.targetHandle
	});
	return edges.filter(function(e) {
		return e.id !== oldEdge.id;
	}).concat(edge);
};
var pointToRendererPoint = function pointToRendererPoint(_ref2, _ref3, snapToGrid, _ref4) {
	var x = _ref2.x, y = _ref2.y;
	var _ref5 = _slicedToArray(_ref3, 3), tx = _ref5[0], ty = _ref5[1], tScale = _ref5[2];
	var _ref6 = _slicedToArray(_ref4, 2), snapX = _ref6[0], snapY = _ref6[1];
	var position = {
		x: (x - tx) / tScale,
		y: (y - ty) / tScale
	};
	if (snapToGrid) return {
		x: snapX * Math.round(position.x / snapX),
		y: snapY * Math.round(position.y / snapY)
	};
	return position;
};
var getRectOfNodes = function getRectOfNodes(nodes) {
	if (nodes.length === 0) return {
		x: 0,
		y: 0,
		width: 0,
		height: 0
	};
	return boxToRect(nodes.reduce(function(currBox, _ref7) {
		var positionAbsolute = _ref7.positionAbsolute, position = _ref7.position, width = _ref7.width, height = _ref7.height;
		return getBoundsOfBoxes(currBox, rectToBox({
			x: positionAbsolute ? positionAbsolute.x : position.x,
			y: positionAbsolute ? positionAbsolute.y : position.y,
			width: width || 0,
			height: height || 0
		}));
	}, {
		x: Infinity,
		y: Infinity,
		x2: -Infinity,
		y2: -Infinity
	}));
};
var getNodesInside = function getNodesInside(nodeInternals, rect) {
	var _ref9 = _slicedToArray(arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : [
		0,
		0,
		1
	], 3), tx = _ref9[0], ty = _ref9[1], tScale = _ref9[2];
	var partially = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : false;
	var excludeNonSelectableNodes = arguments.length > 4 && arguments[4] !== void 0 ? arguments[4] : false;
	var rBox = rectToBox({
		x: (rect.x - tx) / tScale,
		y: (rect.y - ty) / tScale,
		width: rect.width / tScale,
		height: rect.height / tScale
	});
	var visibleNodes = [];
	nodeInternals.forEach(function(node) {
		var positionAbsolute = node.positionAbsolute, width = node.width, height = node.height, _node$selectable = node.selectable;
		if (excludeNonSelectableNodes && !(_node$selectable === void 0 ? true : _node$selectable)) return false;
		var nBox = rectToBox(_objectSpread$2$12(_objectSpread$2$12({}, positionAbsolute), {}, {
			width: width || 0,
			height: height || 0
		}));
		var xOverlap = Math.max(0, Math.min(rBox.x2, nBox.x2) - Math.max(rBox.x, nBox.x));
		var yOverlap = Math.max(0, Math.min(rBox.y2, nBox.y2) - Math.max(rBox.y, nBox.y));
		var overlappingArea = Math.ceil(xOverlap * yOverlap);
		var notInitialized = typeof width === "undefined" || typeof height === "undefined" || width === null || height === null;
		var partiallyVisible = partially && overlappingArea > 0;
		var area = (width || 0) * (height || 0);
		if (notInitialized || partiallyVisible || overlappingArea >= area) visibleNodes.push(node);
	});
	return visibleNodes;
};
var getConnectedEdges = function getConnectedEdges(nodes, edges) {
	var nodeIds = nodes.map(function(node) {
		return node.id;
	});
	return edges.filter(function(edge) {
		return nodeIds.includes(edge.source) || nodeIds.includes(edge.target);
	});
};
var getTransformForBounds = function getTransformForBounds(bounds, width, height, minZoom, maxZoom) {
	var padding = arguments.length > 5 && arguments[5] !== void 0 ? arguments[5] : .1;
	var xZoom = width / (bounds.width * (1 + padding));
	var yZoom = height / (bounds.height * (1 + padding));
	var clampedZoom = clamp(Math.min(xZoom, yZoom), minZoom, maxZoom);
	var boundsCenterX = bounds.x + bounds.width / 2;
	var boundsCenterY = bounds.y + bounds.height / 2;
	return [
		width / 2 - boundsCenterX * clampedZoom,
		height / 2 - boundsCenterY * clampedZoom,
		clampedZoom
	];
};
var getD3Transition = function getD3Transition(selection) {
	var duration = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 0;
	return selection.transition().duration(duration);
};
function ownKeys$1$13(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$1$13(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$1$13(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$1$13(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function calculateXYZPosition(node, nodeInternals, parentNodes, result) {
	var _result$x, _parentNode$position$, _parentNode$position, _result$y, _parentNode$position$2, _parentNode$position2, _parentNode$internals, _parentNode$internals2, _result$z, _parentNode$internals3, _parentNode$internals4, _result$z2;
	if (!node.parentNode) return result;
	var parentNode = nodeInternals.get(node.parentNode);
	return calculateXYZPosition(parentNode, nodeInternals, parentNodes, {
		x: ((_result$x = result.x) !== null && _result$x !== void 0 ? _result$x : 0) + ((_parentNode$position$ = (_parentNode$position = parentNode.position) === null || _parentNode$position === void 0 ? void 0 : _parentNode$position.x) !== null && _parentNode$position$ !== void 0 ? _parentNode$position$ : 0),
		y: ((_result$y = result.y) !== null && _result$y !== void 0 ? _result$y : 0) + ((_parentNode$position$2 = (_parentNode$position2 = parentNode.position) === null || _parentNode$position2 === void 0 ? void 0 : _parentNode$position2.y) !== null && _parentNode$position$2 !== void 0 ? _parentNode$position$2 : 0),
		z: ((_parentNode$internals = (_parentNode$internals2 = parentNode[internalsSymbol]) === null || _parentNode$internals2 === void 0 ? void 0 : _parentNode$internals2.z) !== null && _parentNode$internals !== void 0 ? _parentNode$internals : 0) > ((_result$z = result.z) !== null && _result$z !== void 0 ? _result$z : 0) ? (_parentNode$internals3 = (_parentNode$internals4 = parentNode[internalsSymbol]) === null || _parentNode$internals4 === void 0 ? void 0 : _parentNode$internals4.z) !== null && _parentNode$internals3 !== void 0 ? _parentNode$internals3 : 0 : (_result$z2 = result.z) !== null && _result$z2 !== void 0 ? _result$z2 : 0
	});
}
function createNodeInternals(nodes, nodeInternals) {
	var nextNodeInternals = /* @__PURE__ */ new Map();
	var parentNodes = {};
	nodes.forEach(function(node) {
		var _currInternals$intern;
		var z = isNumeric(node.zIndex) ? node.zIndex : node.selected ? 1e3 : 0;
		var currInternals = nodeInternals.get(node.id);
		var internals = _objectSpread$1$13(_objectSpread$1$13({
			width: currInternals === null || currInternals === void 0 ? void 0 : currInternals.width,
			height: currInternals === null || currInternals === void 0 ? void 0 : currInternals.height
		}, node), {}, { positionAbsolute: {
			x: node.position.x,
			y: node.position.y
		} });
		if (node.parentNode) {
			internals.parentNode = node.parentNode;
			parentNodes[node.parentNode] = true;
		}
		Object.defineProperty(internals, internalsSymbol, {
			enumerable: false,
			value: {
				handleBounds: currInternals === null || currInternals === void 0 ? void 0 : (_currInternals$intern = currInternals[internalsSymbol]) === null || _currInternals$intern === void 0 ? void 0 : _currInternals$intern.handleBounds,
				z
			}
		});
		nextNodeInternals.set(node.id, internals);
	});
	nextNodeInternals.forEach(function(node) {
		if (node.parentNode && !nextNodeInternals.has(node.parentNode)) throw new Error("Parent node ".concat(node.parentNode, " not found"));
		if (node.parentNode || parentNodes[node.id]) {
			var _node$internalsSymbol, _node$internalsSymbol2;
			var _calculateXYZPosition = calculateXYZPosition(node, nextNodeInternals, parentNodes, _objectSpread$1$13(_objectSpread$1$13({}, node.position), {}, { z: (_node$internalsSymbol = (_node$internalsSymbol2 = node[internalsSymbol]) === null || _node$internalsSymbol2 === void 0 ? void 0 : _node$internalsSymbol2.z) !== null && _node$internalsSymbol !== void 0 ? _node$internalsSymbol : 0 })), x = _calculateXYZPosition.x, y = _calculateXYZPosition.y, z = _calculateXYZPosition.z;
			node.positionAbsolute = {
				x,
				y
			};
			node[internalsSymbol].z = z;
			if (parentNodes[node.id]) node[internalsSymbol].isParent = true;
		}
	});
	return nextNodeInternals;
}
function fitView(get) {
	var options = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
	var _get = get(), nodeInternals = _get.nodeInternals, width = _get.width, height = _get.height, minZoom = _get.minZoom, maxZoom = _get.maxZoom, d3Zoom = _get.d3Zoom, d3Selection = _get.d3Selection, fitViewOnInitDone = _get.fitViewOnInitDone, fitViewOnInit = _get.fitViewOnInit;
	if (options.initial && !fitViewOnInitDone && fitViewOnInit || !options.initial) {
		if (d3Zoom && d3Selection) {
			var nodes = Array.from(nodeInternals.values()).filter(function(n) {
				return options.includeHiddenNodes ? n.width && n.height : !n.hidden;
			});
			var nodesInitialized = nodes.every(function(n) {
				return n.width && n.height;
			});
			if (nodes.length > 0 && nodesInitialized) {
				var _options$minZoom, _options$maxZoom, _options$padding;
				var _getTransformForBound2 = _slicedToArray(getTransformForBounds(getRectOfNodes(nodes), width, height, (_options$minZoom = options.minZoom) !== null && _options$minZoom !== void 0 ? _options$minZoom : minZoom, (_options$maxZoom = options.maxZoom) !== null && _options$maxZoom !== void 0 ? _options$maxZoom : maxZoom, (_options$padding = options.padding) !== null && _options$padding !== void 0 ? _options$padding : .1), 3), x = _getTransformForBound2[0], y = _getTransformForBound2[1], zoom = _getTransformForBound2[2];
				var nextTransform = identity.translate(x, y).scale(zoom);
				if (typeof options.duration === "number" && options.duration > 0) d3Zoom.transform(getD3Transition(d3Selection, options.duration), nextTransform);
				else d3Zoom.transform(d3Selection, nextTransform);
				return true;
			}
		}
	}
	return false;
}
function handleControlledNodeSelectionChange(nodeChanges, nodeInternals) {
	nodeChanges.forEach(function(change) {
		var node = nodeInternals.get(change.id);
		if (node) {
			var _objectSpread2;
			nodeInternals.set(node.id, _objectSpread$1$13(_objectSpread$1$13({}, node), {}, (_objectSpread2 = {}, _defineProperty(_objectSpread2, internalsSymbol, node[internalsSymbol]), _defineProperty(_objectSpread2, "selected", change.selected), _objectSpread2)));
		}
	});
	return new Map(nodeInternals);
}
function handleControlledEdgeSelectionChange(edgeChanges, edges) {
	return edges.map(function(e) {
		var change = edgeChanges.find(function(change) {
			return change.id === e.id;
		});
		if (change) e.selected = change.selected;
		return e;
	});
}
function updateNodesAndEdgesSelections(_ref) {
	var changedNodes = _ref.changedNodes, changedEdges = _ref.changedEdges, get = _ref.get, set = _ref.set;
	var _get2 = get(), nodeInternals = _get2.nodeInternals, edges = _get2.edges, onNodesChange = _get2.onNodesChange, onEdgesChange = _get2.onEdgesChange, hasDefaultNodes = _get2.hasDefaultNodes, hasDefaultEdges = _get2.hasDefaultEdges;
	if (changedNodes !== null && changedNodes !== void 0 && changedNodes.length) {
		if (hasDefaultNodes) set({ nodeInternals: handleControlledNodeSelectionChange(changedNodes, nodeInternals) });
		onNodesChange === null || onNodesChange === void 0 || onNodesChange(changedNodes);
	}
	if (changedEdges !== null && changedEdges !== void 0 && changedEdges.length) {
		if (hasDefaultEdges) set({ edges: handleControlledEdgeSelectionChange(changedEdges, edges) });
		onEdgesChange === null || onEdgesChange === void 0 || onEdgesChange(changedEdges);
	}
}
var infiniteExtent = [[Number.NEGATIVE_INFINITY, Number.NEGATIVE_INFINITY], [Number.POSITIVE_INFINITY, Number.POSITIVE_INFINITY]];
var initialState = {
	width: 0,
	height: 0,
	transform: [
		0,
		0,
		1
	],
	nodeInternals: /* @__PURE__ */ new Map(),
	edges: [],
	onNodesChange: null,
	onEdgesChange: null,
	hasDefaultNodes: false,
	hasDefaultEdges: false,
	d3Zoom: null,
	d3Selection: null,
	d3ZoomHandler: void 0,
	minZoom: .5,
	maxZoom: 2,
	translateExtent: infiniteExtent,
	nodeExtent: infiniteExtent,
	nodesSelectionActive: false,
	userSelectionActive: false,
	connectionNodeId: null,
	connectionHandleId: null,
	connectionHandleType: "source",
	connectionPosition: {
		x: 0,
		y: 0
	},
	connectionMode: ConnectionMode.Strict,
	domNode: null,
	snapGrid: [15, 15],
	snapToGrid: false,
	nodesDraggable: true,
	nodesConnectable: true,
	elementsSelectable: true,
	fitViewOnInit: false,
	fitViewOnInitDone: false,
	fitViewOnInitOptions: void 0,
	multiSelectionActive: false,
	reactFlowVersion: "10.3.17",
	connectionStartHandle: null,
	connectOnClick: true
};
function ownKeys$14(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$14(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$14(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$14(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var _createContext = createContext$2(), Provider$1 = _createContext.Provider, useStore = _createContext.useStore, useStoreApi = _createContext.useStoreApi;
var createStore = function createStore() {
	return create$1(function(set, get) {
		return _objectSpread$14(_objectSpread$14({}, initialState), {}, {
			setNodes: function setNodes(nodes) {
				set({ nodeInternals: createNodeInternals(nodes, get().nodeInternals) });
			},
			setEdges: function setEdges(edges) {
				var _get$defaultEdgeOptio = get().defaultEdgeOptions, defaultEdgeOptions = _get$defaultEdgeOptio === void 0 ? {} : _get$defaultEdgeOptio;
				set({ edges: edges.map(function(e) {
					return _objectSpread$14(_objectSpread$14({}, defaultEdgeOptions), e);
				}) });
			},
			setDefaultNodesAndEdges: function setDefaultNodesAndEdges(nodes, edges) {
				var hasDefaultNodes = typeof nodes !== "undefined";
				var hasDefaultEdges = typeof edges !== "undefined";
				set({
					nodeInternals: hasDefaultNodes ? createNodeInternals(nodes, /* @__PURE__ */ new Map()) : /* @__PURE__ */ new Map(),
					edges: hasDefaultEdges ? edges : [],
					hasDefaultNodes,
					hasDefaultEdges
				});
			},
			updateNodeDimensions: function updateNodeDimensions(updates) {
				var _get2 = get(), onNodesChange = _get2.onNodesChange, nodeInternals = _get2.nodeInternals, fitViewOnInit = _get2.fitViewOnInit, fitViewOnInitDone = _get2.fitViewOnInitDone, fitViewOnInitOptions = _get2.fitViewOnInitOptions, domNode = _get2.domNode;
				var viewportNode = domNode === null || domNode === void 0 ? void 0 : domNode.querySelector(".react-flow__viewport");
				if (!viewportNode) return;
				var style = window.getComputedStyle(viewportNode);
				var zoom = new window.DOMMatrixReadOnly(style.transform).m22;
				var changes = updates.reduce(function(res, update) {
					var node = nodeInternals.get(update.id);
					if (node) {
						var dimensions = getDimensions(update.nodeElement);
						if (!!(dimensions.width && dimensions.height && (node.width !== dimensions.width || node.height !== dimensions.height || update.forceUpdate))) {
							nodeInternals.set(node.id, _objectSpread$14(_objectSpread$14({}, node), {}, _defineProperty({}, internalsSymbol, _objectSpread$14(_objectSpread$14({}, node[internalsSymbol]), {}, { handleBounds: {
								source: getHandleBounds(".source", update.nodeElement, zoom),
								target: getHandleBounds(".target", update.nodeElement, zoom)
							} })), dimensions));
							res.push({
								id: node.id,
								type: "dimensions",
								dimensions
							});
						}
					}
					return res;
				}, []);
				var nextFitViewOnInitDone = fitViewOnInitDone || fitViewOnInit && !fitViewOnInitDone && fitView(get, _objectSpread$14({ initial: true }, fitViewOnInitOptions));
				set({
					nodeInternals: new Map(nodeInternals),
					fitViewOnInitDone: nextFitViewOnInitDone
				});
				if ((changes === null || changes === void 0 ? void 0 : changes.length) > 0) onNodesChange === null || onNodesChange === void 0 || onNodesChange(changes);
			},
			updateNodePositions: function updateNodePositions(nodeDragItems) {
				var positionChanged = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : true;
				var dragging = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : false;
				var _get3 = get(), onNodesChange = _get3.onNodesChange, nodeInternals = _get3.nodeInternals, hasDefaultNodes = _get3.hasDefaultNodes;
				if (hasDefaultNodes || onNodesChange) {
					var changes = nodeDragItems.map(function(node) {
						var change = {
							id: node.id,
							type: "position",
							dragging
						};
						if (positionChanged) {
							change.positionAbsolute = node.positionAbsolute;
							change.position = node.position;
						}
						return change;
					});
					if (changes !== null && changes !== void 0 && changes.length) {
						if (hasDefaultNodes) set({ nodeInternals: createNodeInternals(applyNodeChanges(changes, Array.from(nodeInternals.values())), nodeInternals) });
						onNodesChange === null || onNodesChange === void 0 || onNodesChange(changes);
					}
				}
			},
			addSelectedNodes: function addSelectedNodes(selectedNodeIds) {
				var _get4 = get(), multiSelectionActive = _get4.multiSelectionActive, nodeInternals = _get4.nodeInternals, edges = _get4.edges;
				var changedNodes;
				var changedEdges = null;
				if (multiSelectionActive) changedNodes = selectedNodeIds.map(function(nodeId) {
					return createSelectionChange(nodeId, true);
				});
				else {
					changedNodes = getSelectionChanges(Array.from(nodeInternals.values()), selectedNodeIds);
					changedEdges = getSelectionChanges(edges, []);
				}
				updateNodesAndEdgesSelections({
					changedNodes,
					changedEdges,
					get,
					set
				});
			},
			addSelectedEdges: function addSelectedEdges(selectedEdgeIds) {
				var _get5 = get(), multiSelectionActive = _get5.multiSelectionActive, edges = _get5.edges, nodeInternals = _get5.nodeInternals;
				var changedEdges;
				var changedNodes = null;
				if (multiSelectionActive) changedEdges = selectedEdgeIds.map(function(edgeId) {
					return createSelectionChange(edgeId, true);
				});
				else {
					changedEdges = getSelectionChanges(edges, selectedEdgeIds);
					changedNodes = getSelectionChanges(Array.from(nodeInternals.values()), []);
				}
				updateNodesAndEdgesSelections({
					changedNodes,
					changedEdges,
					get,
					set
				});
			},
			unselectNodesAndEdges: function unselectNodesAndEdges() {
				var _ref = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {}, nodes = _ref.nodes, edges = _ref.edges;
				var _get6 = get(), nodeInternals = _get6.nodeInternals, storeEdges = _get6.edges;
				var nodesToUnselect = nodes ? nodes : Array.from(nodeInternals.values());
				var edgesToUnselect = edges ? edges : storeEdges;
				updateNodesAndEdgesSelections({
					changedNodes: nodesToUnselect.map(function(n) {
						n.selected = false;
						return createSelectionChange(n.id, false);
					}),
					changedEdges: edgesToUnselect.map(function(edge) {
						return createSelectionChange(edge.id, false);
					}),
					get,
					set
				});
			},
			setMinZoom: function setMinZoom(minZoom) {
				var _get7 = get(), d3Zoom = _get7.d3Zoom, maxZoom = _get7.maxZoom;
				d3Zoom === null || d3Zoom === void 0 || d3Zoom.scaleExtent([minZoom, maxZoom]);
				set({ minZoom });
			},
			setMaxZoom: function setMaxZoom(maxZoom) {
				var _get8 = get(), d3Zoom = _get8.d3Zoom, minZoom = _get8.minZoom;
				d3Zoom === null || d3Zoom === void 0 || d3Zoom.scaleExtent([minZoom, maxZoom]);
				set({ maxZoom });
			},
			setTranslateExtent: function setTranslateExtent(translateExtent) {
				var d3Zoom = get().d3Zoom;
				d3Zoom === null || d3Zoom === void 0 || d3Zoom.translateExtent(translateExtent);
				set({ translateExtent });
			},
			resetSelectedElements: function resetSelectedElements() {
				var _get10 = get(), nodeInternals = _get10.nodeInternals, edges = _get10.edges;
				updateNodesAndEdgesSelections({
					changedNodes: Array.from(nodeInternals.values()).filter(function(e) {
						return e.selected;
					}).map(function(n) {
						return createSelectionChange(n.id, false);
					}),
					changedEdges: edges.filter(function(e) {
						return e.selected;
					}).map(function(e) {
						return createSelectionChange(e.id, false);
					}),
					get,
					set
				});
			},
			setNodeExtent: function setNodeExtent(nodeExtent) {
				var nodeInternals = get().nodeInternals;
				nodeInternals.forEach(function(node) {
					node.positionAbsolute = clampPosition(node.position, nodeExtent);
				});
				set({
					nodeExtent,
					nodeInternals: new Map(nodeInternals)
				});
			},
			reset: function reset() {
				return set(_objectSpread$14({}, initialState));
			}
		});
	});
};
//#endregion
//#region node_modules/classcat/index.js
function cc(names) {
	if (typeof names === "string" || typeof names === "number") return "" + names;
	let out = "";
	if (Array.isArray(names)) {
		for (let i = 0, tmp; i < names.length; i++) if ((tmp = cc(names[i])) !== "") out += (out && " ") + tmp;
	} else for (let k in names) if (names[k]) out += (out && " ") + k;
	return out;
}
//#endregion
//#region node_modules/react-flow-renderer/node_modules/zustand/esm/shallow.js
function shallow(objA, objB) {
	if (Object.is(objA, objB)) return true;
	if (typeof objA !== "object" || objA === null || typeof objB !== "object" || objB === null) return false;
	const keysA = Object.keys(objA);
	if (keysA.length !== Object.keys(objB).length) return false;
	for (let i = 0; i < keysA.length; i++) if (!Object.prototype.hasOwnProperty.call(objB, keysA[i]) || !Object.is(objA[keysA[i]], objB[keysA[i]])) return false;
	return true;
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/useReactFlow-993c30ca.js
function _arrayWithoutHoles(arr) {
	if (Array.isArray(arr)) return _arrayLikeToArray(arr);
}
function _iterableToArray(iter) {
	if (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null || iter["@@iterator"] != null) return Array.from(iter);
}
function _nonIterableSpread() {
	throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
}
function _toConsumableArray(arr) {
	return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread();
}
var initialViewportHelper = {
	zoomIn: function zoomIn() {},
	zoomOut: function zoomOut() {},
	zoomTo: function zoomTo(_) {},
	getZoom: function getZoom() {
		return 1;
	},
	setViewport: function setViewport(_) {},
	getViewport: function getViewport() {
		return {
			x: 0,
			y: 0,
			zoom: 1
		};
	},
	fitView: function fitView() {},
	setCenter: function setCenter(_, __) {},
	fitBounds: function fitBounds(_) {},
	project: function project(position) {
		return position;
	},
	viewportInitialized: false
};
var selector$12 = function selector(s) {
	return {
		d3Zoom: s.d3Zoom,
		d3Selection: s.d3Selection
	};
};
var useViewportHelper = function useViewportHelper() {
	var store = useStoreApi();
	var _useStore = useStore(selector$12, shallow), d3Zoom = _useStore.d3Zoom, d3Selection = _useStore.d3Selection;
	return (0, import_react.useMemo)(function() {
		if (d3Selection && d3Zoom) return {
			zoomIn: function zoomIn(options) {
				return d3Zoom.scaleBy(getD3Transition(d3Selection, options === null || options === void 0 ? void 0 : options.duration), 1.2);
			},
			zoomOut: function zoomOut(options) {
				return d3Zoom.scaleBy(getD3Transition(d3Selection, options === null || options === void 0 ? void 0 : options.duration), 1 / 1.2);
			},
			zoomTo: function zoomTo(zoomLevel, options) {
				return d3Zoom.scaleTo(getD3Transition(d3Selection, options === null || options === void 0 ? void 0 : options.duration), zoomLevel);
			},
			getZoom: function getZoom() {
				return store.getState().transform[2];
			},
			setViewport: function setViewport(transform, options) {
				var _transform$x, _transform$y, _transform$zoom;
				var _store$getState$trans = _slicedToArray(store.getState().transform, 3), x = _store$getState$trans[0], y = _store$getState$trans[1], zoom = _store$getState$trans[2];
				var nextTransform = identity.translate((_transform$x = transform.x) !== null && _transform$x !== void 0 ? _transform$x : x, (_transform$y = transform.y) !== null && _transform$y !== void 0 ? _transform$y : y).scale((_transform$zoom = transform.zoom) !== null && _transform$zoom !== void 0 ? _transform$zoom : zoom);
				d3Zoom.transform(getD3Transition(d3Selection, options === null || options === void 0 ? void 0 : options.duration), nextTransform);
			},
			getViewport: function getViewport() {
				var _store$getState$trans2 = _slicedToArray(store.getState().transform, 3);
				return {
					x: _store$getState$trans2[0],
					y: _store$getState$trans2[1],
					zoom: _store$getState$trans2[2]
				};
			},
			fitView: function fitView$1(options) {
				return fitView(store.getState, options);
			},
			setCenter: function setCenter(x, y, options) {
				var _store$getState = store.getState(), width = _store$getState.width, height = _store$getState.height, maxZoom = _store$getState.maxZoom;
				var nextZoom = typeof (options === null || options === void 0 ? void 0 : options.zoom) !== "undefined" ? options.zoom : maxZoom;
				var centerX = width / 2 - x * nextZoom;
				var centerY = height / 2 - y * nextZoom;
				var transform = identity.translate(centerX, centerY).scale(nextZoom);
				d3Zoom.transform(getD3Transition(d3Selection, options === null || options === void 0 ? void 0 : options.duration), transform);
			},
			fitBounds: function fitBounds(bounds, options) {
				var _options$padding;
				var _store$getState2 = store.getState(), width = _store$getState2.width, height = _store$getState2.height, minZoom = _store$getState2.minZoom, maxZoom = _store$getState2.maxZoom;
				var _getTransformForBound2 = _slicedToArray(getTransformForBounds(bounds, width, height, minZoom, maxZoom, (_options$padding = options === null || options === void 0 ? void 0 : options.padding) !== null && _options$padding !== void 0 ? _options$padding : .1), 3), x = _getTransformForBound2[0], y = _getTransformForBound2[1], zoom = _getTransformForBound2[2];
				var transform = identity.translate(x, y).scale(zoom);
				d3Zoom.transform(getD3Transition(d3Selection, options === null || options === void 0 ? void 0 : options.duration), transform);
			},
			project: function project(position) {
				var _store$getState3 = store.getState(), transform = _store$getState3.transform, snapToGrid = _store$getState3.snapToGrid, snapGrid = _store$getState3.snapGrid;
				return pointToRendererPoint(position, transform, snapToGrid, snapGrid);
			},
			viewportInitialized: true
		};
		return initialViewportHelper;
	}, [d3Zoom, d3Selection]);
};
function ownKeys$12(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$12(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$12(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$12(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function useReactFlow() {
	var viewportHelper = useViewportHelper();
	var store = useStoreApi();
	var getNodes = (0, import_react.useCallback)(function() {
		var nodeInternals = store.getState().nodeInternals;
		return Array.from(nodeInternals.values()).map(function(n) {
			return _objectSpread$12({}, n);
		});
	}, []);
	var getNode = (0, import_react.useCallback)(function(id) {
		return store.getState().nodeInternals.get(id);
	}, []);
	var getEdges = (0, import_react.useCallback)(function() {
		var _store$getState3$edge = store.getState().edges;
		return (_store$getState3$edge === void 0 ? [] : _store$getState3$edge).map(function(e) {
			return _objectSpread$12({}, e);
		});
	}, []);
	var getEdge = (0, import_react.useCallback)(function(id) {
		var _store$getState4$edge = store.getState().edges;
		return (_store$getState4$edge === void 0 ? [] : _store$getState4$edge).find(function(e) {
			return e.id === id;
		});
	}, []);
	var setNodes = (0, import_react.useCallback)(function(payload) {
		var _store$getState5 = store.getState(), nodeInternals = _store$getState5.nodeInternals, setNodes = _store$getState5.setNodes, hasDefaultNodes = _store$getState5.hasDefaultNodes, onNodesChange = _store$getState5.onNodesChange;
		var nodes = Array.from(nodeInternals.values());
		var nextNodes = typeof payload === "function" ? payload(nodes) : payload;
		if (hasDefaultNodes) setNodes(nextNodes);
		else if (onNodesChange) onNodesChange(nextNodes.length === 0 ? nodes.map(function(node) {
			return {
				type: "remove",
				id: node.id
			};
		}) : nextNodes.map(function(node) {
			return {
				item: node,
				type: "reset"
			};
		}));
	}, []);
	var setEdges = (0, import_react.useCallback)(function(payload) {
		var _store$getState6 = store.getState(), _store$getState6$edge = _store$getState6.edges, edges = _store$getState6$edge === void 0 ? [] : _store$getState6$edge, setEdges = _store$getState6.setEdges, hasDefaultEdges = _store$getState6.hasDefaultEdges, onEdgesChange = _store$getState6.onEdgesChange;
		var nextEdges = typeof payload === "function" ? payload(edges) : payload;
		if (hasDefaultEdges) setEdges(nextEdges);
		else if (onEdgesChange) onEdgesChange(nextEdges.length === 0 ? edges.map(function(edge) {
			return {
				type: "remove",
				id: edge.id
			};
		}) : nextEdges.map(function(edge) {
			return {
				item: edge,
				type: "reset"
			};
		}));
	}, []);
	var addNodes = (0, import_react.useCallback)(function(payload) {
		var nodes = Array.isArray(payload) ? payload : [payload];
		var _store$getState7 = store.getState(), nodeInternals = _store$getState7.nodeInternals, setNodes = _store$getState7.setNodes, hasDefaultNodes = _store$getState7.hasDefaultNodes, onNodesChange = _store$getState7.onNodesChange;
		if (hasDefaultNodes) {
			var currentNodes = Array.from(nodeInternals.values());
			setNodes([].concat(currentNodes, _toConsumableArray(nodes)));
		} else if (onNodesChange) onNodesChange(nodes.map(function(node) {
			return {
				item: node,
				type: "add"
			};
		}));
	}, []);
	var addEdges = (0, import_react.useCallback)(function(payload) {
		var nextEdges = Array.isArray(payload) ? payload : [payload];
		var _store$getState8 = store.getState(), _store$getState8$edge = _store$getState8.edges, edges = _store$getState8$edge === void 0 ? [] : _store$getState8$edge, setEdges = _store$getState8.setEdges, hasDefaultEdges = _store$getState8.hasDefaultEdges, onEdgesChange = _store$getState8.onEdgesChange;
		if (hasDefaultEdges) setEdges([].concat(_toConsumableArray(edges), _toConsumableArray(nextEdges)));
		else if (onEdgesChange) onEdgesChange(nextEdges.map(function(edge) {
			return {
				item: edge,
				type: "add"
			};
		}));
	}, []);
	var toObject = (0, import_react.useCallback)(function() {
		var _store$getState9 = store.getState(), nodeInternals = _store$getState9.nodeInternals, _store$getState9$edge = _store$getState9.edges, edges = _store$getState9$edge === void 0 ? [] : _store$getState9$edge, transform = _store$getState9.transform;
		var nodes = Array.from(nodeInternals.values());
		var _transform = _slicedToArray(transform, 3), x = _transform[0], y = _transform[1], zoom = _transform[2];
		return {
			nodes: nodes.map(function(n) {
				return _objectSpread$12({}, n);
			}),
			edges: edges.map(function(e) {
				return _objectSpread$12({}, e);
			}),
			viewport: {
				x,
				y,
				zoom
			}
		};
	}, []);
	return (0, import_react.useMemo)(function() {
		return _objectSpread$12(_objectSpread$12({}, viewportHelper), {}, {
			getNodes,
			getNode,
			getEdges,
			getEdge,
			setNodes,
			setEdges,
			addNodes,
			addEdges,
			toObject
		});
	}, [
		viewportHelper,
		getNodes,
		getNode,
		getEdges,
		getEdge,
		setNodes,
		setEdges,
		addNodes,
		addEdges,
		toObject
	]);
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/index-20df97c0.js
function _objectWithoutPropertiesLoose(source, excluded) {
	if (source == null) return {};
	var target = {};
	var sourceKeys = Object.keys(source);
	var key, i;
	for (i = 0; i < sourceKeys.length; i++) {
		key = sourceKeys[i];
		if (excluded.indexOf(key) >= 0) continue;
		target[key] = source[key];
	}
	return target;
}
function _objectWithoutProperties(source, excluded) {
	if (source == null) return {};
	var target = _objectWithoutPropertiesLoose(source, excluded);
	var key, i;
	if (Object.getOwnPropertySymbols) {
		var sourceSymbolKeys = Object.getOwnPropertySymbols(source);
		for (i = 0; i < sourceSymbolKeys.length; i++) {
			key = sourceSymbolKeys[i];
			if (excluded.indexOf(key) >= 0) continue;
			if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue;
			target[key] = source[key];
		}
	}
	return target;
}
function PlusIcon() {
	return /* @__PURE__ */ import_react.createElement("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 32 32"
	}, /* @__PURE__ */ import_react.createElement("path", { d: "M32 18.133H18.133V32h-4.266V18.133H0v-4.266h13.867V0h4.266v13.867H32z" }));
}
function MinusIcon() {
	return /* @__PURE__ */ import_react.createElement("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 32 5"
	}, /* @__PURE__ */ import_react.createElement("path", { d: "M0 0h32v4.2H0z" }));
}
function FitViewIcon() {
	return /* @__PURE__ */ import_react.createElement("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 32 30"
	}, /* @__PURE__ */ import_react.createElement("path", { d: "M3.692 4.63c0-.53.4-.938.939-.938h5.215V0H4.708C2.13 0 0 2.054 0 4.63v5.216h3.692V4.631zM27.354 0h-5.2v3.692h5.17c.53 0 .984.4.984.939v5.215H32V4.631A4.624 4.624 0 0027.354 0zm.954 24.83c0 .532-.4.94-.939.94h-5.215v3.768h5.215c2.577 0 4.631-2.13 4.631-4.707v-5.139h-3.692v5.139zm-23.677.94c-.531 0-.939-.4-.939-.94v-5.138H0v5.139c0 2.577 2.13 4.707 4.708 4.707h5.138V25.77H4.631z" }));
}
function LockIcon() {
	return /* @__PURE__ */ import_react.createElement("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 25 32"
	}, /* @__PURE__ */ import_react.createElement("path", { d: "M21.333 10.667H19.81V7.619C19.81 3.429 16.38 0 12.19 0 8 0 4.571 3.429 4.571 7.619v3.048H3.048A3.056 3.056 0 000 13.714v15.238A3.056 3.056 0 003.048 32h18.285a3.056 3.056 0 003.048-3.048V13.714a3.056 3.056 0 00-3.048-3.047zM12.19 24.533a3.056 3.056 0 01-3.047-3.047 3.056 3.056 0 013.047-3.048 3.056 3.056 0 013.048 3.048 3.056 3.056 0 01-3.048 3.047zm4.724-13.866H7.467V7.619c0-2.59 2.133-4.724 4.723-4.724 2.591 0 4.724 2.133 4.724 4.724v3.048z" }));
}
function UnlockIcon() {
	return /* @__PURE__ */ import_react.createElement("svg", {
		xmlns: "http://www.w3.org/2000/svg",
		viewBox: "0 0 25 32"
	}, /* @__PURE__ */ import_react.createElement("path", { d: "M21.333 10.667H19.81V7.619C19.81 3.429 16.38 0 12.19 0c-4.114 1.828-1.37 2.133.305 2.438 1.676.305 4.42 2.59 4.42 5.181v3.048H3.047A3.056 3.056 0 000 13.714v15.238A3.056 3.056 0 003.048 32h18.285a3.056 3.056 0 003.048-3.048V13.714a3.056 3.056 0 00-3.048-3.047zM12.19 24.533a3.056 3.056 0 01-3.047-3.047 3.056 3.056 0 013.047-3.048 3.056 3.056 0 013.048 3.048 3.056 3.056 0 01-3.048 3.047z" }));
}
var _excluded$3 = ["children", "className"];
function ownKeys$11(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$11(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$11(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$11(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var ControlButton = function ControlButton(_ref) {
	var children = _ref.children, className = _ref.className, rest = _objectWithoutProperties(_ref, _excluded$3);
	return /* @__PURE__ */ import_react.createElement("button", _objectSpread$11({
		type: "button",
		className: cc(["react-flow__controls-button", className])
	}, rest), children);
};
var isInteractiveSelector = function isInteractiveSelector(s) {
	return s.nodesDraggable && s.nodesConnectable && s.elementsSelectable;
};
var Controls = function Controls(_ref2) {
	var style = _ref2.style, _ref2$showZoom = _ref2.showZoom, showZoom = _ref2$showZoom === void 0 ? true : _ref2$showZoom, _ref2$showFitView = _ref2.showFitView, showFitView = _ref2$showFitView === void 0 ? true : _ref2$showFitView, _ref2$showInteractive = _ref2.showInteractive, showInteractive = _ref2$showInteractive === void 0 ? true : _ref2$showInteractive, fitViewOptions = _ref2.fitViewOptions, onZoomIn = _ref2.onZoomIn, onZoomOut = _ref2.onZoomOut, onFitView = _ref2.onFitView, onInteractiveChange = _ref2.onInteractiveChange, className = _ref2.className, children = _ref2.children;
	var store = useStoreApi();
	var _useState2 = _slicedToArray((0, import_react.useState)(false), 2), isVisible = _useState2[0], setIsVisible = _useState2[1];
	var isInteractive = useStore(isInteractiveSelector);
	var _useReactFlow = useReactFlow(), zoomIn = _useReactFlow.zoomIn, zoomOut = _useReactFlow.zoomOut, fitView = _useReactFlow.fitView;
	(0, import_react.useEffect)(function() {
		setIsVisible(true);
	}, []);
	if (!isVisible) return null;
	var onZoomInHandler = function onZoomInHandler() {
		zoomIn === null || zoomIn === void 0 || zoomIn();
		onZoomIn === null || onZoomIn === void 0 || onZoomIn();
	};
	var onZoomOutHandler = function onZoomOutHandler() {
		zoomOut === null || zoomOut === void 0 || zoomOut();
		onZoomOut === null || onZoomOut === void 0 || onZoomOut();
	};
	var onFitViewHandler = function onFitViewHandler() {
		fitView === null || fitView === void 0 || fitView(fitViewOptions);
		onFitView === null || onFitView === void 0 || onFitView();
	};
	var onToggleInteractivity = function onToggleInteractivity() {
		store.setState({
			nodesDraggable: !isInteractive,
			nodesConnectable: !isInteractive,
			elementsSelectable: !isInteractive
		});
		onInteractiveChange === null || onInteractiveChange === void 0 || onInteractiveChange(!isInteractive);
	};
	return /* @__PURE__ */ import_react.createElement("div", {
		className: cc(["react-flow__controls", className]),
		style
	}, showZoom && /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, /* @__PURE__ */ import_react.createElement(ControlButton, {
		onClick: onZoomInHandler,
		className: "react-flow__controls-zoomin",
		title: "zoom in",
		"aria-label": "zoom in"
	}, /* @__PURE__ */ import_react.createElement(PlusIcon, null)), /* @__PURE__ */ import_react.createElement(ControlButton, {
		onClick: onZoomOutHandler,
		className: "react-flow__controls-zoomout",
		title: "zoom out",
		"aria-label": "zoom out"
	}, /* @__PURE__ */ import_react.createElement(MinusIcon, null))), showFitView && /* @__PURE__ */ import_react.createElement(ControlButton, {
		className: "react-flow__controls-fitview",
		onClick: onFitViewHandler,
		title: "fit view",
		"aria-label": "fit view"
	}, /* @__PURE__ */ import_react.createElement(FitViewIcon, null)), showInteractive && /* @__PURE__ */ import_react.createElement(ControlButton, {
		className: "react-flow__controls-interactive",
		onClick: onToggleInteractivity,
		title: "toggle interactivity",
		"aria-label": "toggle interactivity"
	}, isInteractive ? /* @__PURE__ */ import_react.createElement(UnlockIcon, null) : /* @__PURE__ */ import_react.createElement(LockIcon, null)), children);
};
Controls.displayName = "Controls";
var index$1 = /* @__PURE__ */ (0, import_react.memo)(Controls);
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/index2.js
var MiniMapNode = function MiniMapNode(_ref) {
	var x = _ref.x, y = _ref.y, width = _ref.width, height = _ref.height, style = _ref.style, color = _ref.color, strokeColor = _ref.strokeColor, strokeWidth = _ref.strokeWidth, className = _ref.className, borderRadius = _ref.borderRadius, shapeRendering = _ref.shapeRendering;
	var _ref2 = style || {}, background = _ref2.background, backgroundColor = _ref2.backgroundColor;
	var fill = color || background || backgroundColor;
	return /* @__PURE__ */ import_react.createElement("rect", {
		className: cc(["react-flow__minimap-node", className]),
		x,
		y,
		rx: borderRadius,
		ry: borderRadius,
		width,
		height,
		fill,
		stroke: strokeColor,
		strokeWidth,
		shapeRendering
	});
};
MiniMapNode.displayName = "MiniMapNode";
var MiniMapNode$1 = /* @__PURE__ */ (0, import_react.memo)(MiniMapNode);
var defaultWidth = 200;
var defaultHeight = 150;
var selector$11 = function selector(s) {
	return {
		viewBBox: {
			x: -s.transform[0] / s.transform[2],
			y: -s.transform[1] / s.transform[2],
			width: s.width / s.transform[2],
			height: s.height / s.transform[2]
		},
		nodes: Array.from(s.nodeInternals.values())
	};
};
var getAttrFunction = function getAttrFunction(func) {
	return func instanceof Function ? func : function() {
		return func;
	};
};
var MiniMap = function MiniMap(_ref) {
	var _style$width, _style$height;
	var style = _ref.style, className = _ref.className, _ref$nodeStrokeColor = _ref.nodeStrokeColor, nodeStrokeColor = _ref$nodeStrokeColor === void 0 ? "#555" : _ref$nodeStrokeColor, _ref$nodeColor = _ref.nodeColor, nodeColor = _ref$nodeColor === void 0 ? "#fff" : _ref$nodeColor, _ref$nodeClassName = _ref.nodeClassName, nodeClassName = _ref$nodeClassName === void 0 ? "" : _ref$nodeClassName, _ref$nodeBorderRadius = _ref.nodeBorderRadius, nodeBorderRadius = _ref$nodeBorderRadius === void 0 ? 5 : _ref$nodeBorderRadius, _ref$nodeStrokeWidth = _ref.nodeStrokeWidth, nodeStrokeWidth = _ref$nodeStrokeWidth === void 0 ? 2 : _ref$nodeStrokeWidth, _ref$maskColor = _ref.maskColor, maskColor = _ref$maskColor === void 0 ? "rgb(240, 242, 243, 0.7)" : _ref$maskColor;
	var _useStore = useStore(selector$11, shallow), viewBBox = _useStore.viewBBox, nodes = _useStore.nodes;
	var elementWidth = (_style$width = style === null || style === void 0 ? void 0 : style.width) !== null && _style$width !== void 0 ? _style$width : defaultWidth;
	var elementHeight = (_style$height = style === null || style === void 0 ? void 0 : style.height) !== null && _style$height !== void 0 ? _style$height : defaultHeight;
	var nodeColorFunc = getAttrFunction(nodeColor);
	var nodeStrokeColorFunc = getAttrFunction(nodeStrokeColor);
	var nodeClassNameFunc = getAttrFunction(nodeClassName);
	var boundingRect = nodes.length > 0 ? getBoundsofRects(getRectOfNodes(nodes), viewBBox) : viewBBox;
	var scaledWidth = boundingRect.width / elementWidth;
	var scaledHeight = boundingRect.height / elementHeight;
	var viewScale = Math.max(scaledWidth, scaledHeight);
	var viewWidth = viewScale * elementWidth;
	var viewHeight = viewScale * elementHeight;
	var offset = 5 * viewScale;
	var x = boundingRect.x - (viewWidth - boundingRect.width) / 2 - offset;
	var y = boundingRect.y - (viewHeight - boundingRect.height) / 2 - offset;
	var width = viewWidth + offset * 2;
	var height = viewHeight + offset * 2;
	var shapeRendering = typeof window === "undefined" || !!window.chrome ? "crispEdges" : "geometricPrecision";
	return /* @__PURE__ */ import_react.createElement("svg", {
		width: elementWidth,
		height: elementHeight,
		viewBox: "".concat(x, " ").concat(y, " ").concat(width, " ").concat(height),
		style,
		className: cc(["react-flow__minimap", className])
	}, nodes.filter(function(node) {
		return !node.hidden && node.width && node.height;
	}).map(function(node) {
		var _node$positionAbsolut, _node$positionAbsolut2, _node$positionAbsolut3, _node$positionAbsolut4;
		return /* @__PURE__ */ import_react.createElement(MiniMapNode$1, {
			key: node.id,
			x: (_node$positionAbsolut = (_node$positionAbsolut2 = node.positionAbsolute) === null || _node$positionAbsolut2 === void 0 ? void 0 : _node$positionAbsolut2.x) !== null && _node$positionAbsolut !== void 0 ? _node$positionAbsolut : 0,
			y: (_node$positionAbsolut3 = (_node$positionAbsolut4 = node.positionAbsolute) === null || _node$positionAbsolut4 === void 0 ? void 0 : _node$positionAbsolut4.y) !== null && _node$positionAbsolut3 !== void 0 ? _node$positionAbsolut3 : 0,
			width: node.width,
			height: node.height,
			style: node.style,
			className: nodeClassNameFunc(node),
			color: nodeColorFunc(node),
			borderRadius: nodeBorderRadius,
			strokeColor: nodeStrokeColorFunc(node),
			strokeWidth: nodeStrokeWidth,
			shapeRendering
		});
	}), /* @__PURE__ */ import_react.createElement("path", {
		className: "react-flow__minimap-mask",
		d: "M".concat(x - offset, ",").concat(y - offset, "h").concat(width + offset * 2, "v").concat(height + offset * 2, "h").concat(-width - offset * 2, "z\n        M").concat(viewBBox.x, ",").concat(viewBBox.y, "h").concat(viewBBox.width, "v").concat(viewBBox.height, "h").concat(-viewBBox.width, "z"),
		fill: maskColor,
		fillRule: "evenodd"
	}));
};
MiniMap.displayName = "MiniMap";
var index$2 = /* @__PURE__ */ (0, import_react.memo)(MiniMap);
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/index3.js
var createGridLinesPath = function createGridLinesPath(size, strokeWidth, stroke) {
	return /* @__PURE__ */ import_react.createElement("path", {
		stroke,
		strokeWidth,
		d: "M".concat(size / 2, " 0 V").concat(size, " M0 ").concat(size / 2, " H").concat(size)
	});
};
var createGridDotsPath = function createGridDotsPath(size, fill) {
	return /* @__PURE__ */ import_react.createElement("circle", {
		cx: size,
		cy: size,
		r: size,
		fill
	});
};
var _defaultColors;
function ownKeys$10(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$10(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$10(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$10(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var defaultColors = (_defaultColors = {}, _defineProperty(_defaultColors, BackgroundVariant.Dots, "#81818a"), _defineProperty(_defaultColors, BackgroundVariant.Lines, "#eee"), _defaultColors);
var transformSelector = function transformSelector(s) {
	return s.transform;
};
var Background = function Background(_ref) {
	var _ref$variant = _ref.variant, variant = _ref$variant === void 0 ? BackgroundVariant.Dots : _ref$variant, _ref$gap = _ref.gap, gap = _ref$gap === void 0 ? 15 : _ref$gap, _ref$size = _ref.size, size = _ref$size === void 0 ? .4 : _ref$size, color = _ref.color, style = _ref.style, className = _ref.className;
	var ref = (0, import_react.useRef)(null);
	var _useState2 = _slicedToArray((0, import_react.useState)(null), 2), patternId = _useState2[0], setPatternId = _useState2[1];
	var _useStore2 = _slicedToArray(useStore(transformSelector), 3), tX = _useStore2[0], tY = _useStore2[1], tScale = _useStore2[2];
	(0, import_react.useEffect)(function() {
		var bgs = document.querySelectorAll(".react-flow__background");
		var index = Array.from(bgs).findIndex(function(bg) {
			return bg === ref.current;
		});
		setPatternId("pattern-".concat(index));
	}, []);
	var scaledGap = gap * tScale || 1;
	var xOffset = tX % scaledGap;
	var yOffset = tY % scaledGap;
	var isLines = variant === BackgroundVariant.Lines;
	var bgColor = color ? color : defaultColors[variant];
	var path = isLines ? createGridLinesPath(scaledGap, size, bgColor) : createGridDotsPath(size * tScale, bgColor);
	return /* @__PURE__ */ import_react.createElement("svg", {
		className: cc([
			"react-flow__background",
			"react-flow__container",
			className
		]),
		style: _objectSpread$10(_objectSpread$10({}, style), {}, {
			width: "100%",
			height: "100%"
		}),
		ref
	}, patternId && /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, /* @__PURE__ */ import_react.createElement("pattern", {
		id: patternId,
		x: xOffset,
		y: yOffset,
		width: scaledGap,
		height: scaledGap,
		patternUnits: "userSpaceOnUse"
	}, path), /* @__PURE__ */ import_react.createElement("rect", {
		x: "0",
		y: "0",
		width: "100%",
		height: "100%",
		fill: "url(#".concat(patternId, ")")
	})));
};
Background.displayName = "Background";
var index = /* @__PURE__ */ (0, import_react.memo)(Background);
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/useUpdateNodeInternals.js
var selector$10 = function selector(state) {
	return state.updateNodeDimensions;
};
function useUpdateNodeInternals() {
	var store = useStoreApi();
	var updateNodeDimensions = useStore(selector$10);
	return (0, import_react.useCallback)(function(id) {
		var _store$getState$domNo;
		var nodeElement = (_store$getState$domNo = store.getState().domNode) === null || _store$getState$domNo === void 0 ? void 0 : _store$getState$domNo.querySelector(".react-flow__node[data-id=\"".concat(id, "\"]"));
		if (nodeElement) requestAnimationFrame(function() {
			return updateNodeDimensions([{
				id,
				nodeElement,
				forceUpdate: true
			}]);
		});
	}, []);
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/useNodes.js
var nodesSelector = function nodesSelector(state) {
	return Array.from(state.nodeInternals.values());
};
function useNodes() {
	return useStore(nodesSelector);
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/useEdges.js
var edgesSelector = function edgesSelector(state) {
	return state.edges;
};
function useEdges() {
	return useStore(edgesSelector);
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/useViewport.js
var viewportSelector = function viewportSelector(state) {
	return {
		x: state.transform[0],
		y: state.transform[1],
		zoom: state.transform[2]
	};
};
function useViewport() {
	return useStore(viewportSelector, shallow);
}
//#endregion
//#region node_modules/react-flow-renderer/dist/esm/index.js
var accounts = [
	"paid-pro",
	"paid-sponsor",
	"paid-enterprise",
	"paid-custom"
];
function Attribution(_ref) {
	var proOptions = _ref.proOptions, _ref$position = _ref.position, position = _ref$position === void 0 ? "bottom-right" : _ref$position;
	if (proOptions !== null && proOptions !== void 0 && proOptions.account && accounts.includes(proOptions === null || proOptions === void 0 ? void 0 : proOptions.account) && proOptions !== null && proOptions !== void 0 && proOptions.hideAttribution) return null;
	var positionClasses = "".concat(position).split("-");
	return /* @__PURE__ */ import_react.createElement("div", {
		className: cc(["react-flow__attribution"].concat(_toConsumableArray(positionClasses))),
		"data-message": "Please only hide this attribution when you are subscribed to React Flow Pro: https://pro.reactflow.dev/pricing"
	}, /* @__PURE__ */ import_react.createElement("a", {
		href: "https://reactflow.dev",
		target: "_blank",
		rel: "noopener noreferrer"
	}, "React Flow"));
}
var _excluded$2 = [
	"x",
	"y",
	"label",
	"labelStyle",
	"labelShowBg",
	"labelBgStyle",
	"labelBgPadding",
	"labelBgBorderRadius",
	"children",
	"className"
];
function ownKeys$c(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$c(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$c(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$c(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var EdgeText$1 = /* @__PURE__ */ (0, import_react.memo)(function EdgeText(_ref) {
	var x = _ref.x, y = _ref.y, label = _ref.label, _ref$labelStyle = _ref.labelStyle, labelStyle = _ref$labelStyle === void 0 ? {} : _ref$labelStyle, _ref$labelShowBg = _ref.labelShowBg, labelShowBg = _ref$labelShowBg === void 0 ? true : _ref$labelShowBg, _ref$labelBgStyle = _ref.labelBgStyle, labelBgStyle = _ref$labelBgStyle === void 0 ? {} : _ref$labelBgStyle, _ref$labelBgPadding = _ref.labelBgPadding, labelBgPadding = _ref$labelBgPadding === void 0 ? [2, 4] : _ref$labelBgPadding, _ref$labelBgBorderRad = _ref.labelBgBorderRadius, labelBgBorderRadius = _ref$labelBgBorderRad === void 0 ? 2 : _ref$labelBgBorderRad, children = _ref.children, className = _ref.className, rest = _objectWithoutProperties(_ref, _excluded$2);
	var edgeRef = (0, import_react.useRef)(null);
	var _useState2 = _slicedToArray((0, import_react.useState)({
		x: 0,
		y: 0,
		width: 0,
		height: 0
	}), 2), edgeTextBbox = _useState2[0], setEdgeTextBbox = _useState2[1];
	var edgeTextClasses = cc(["react-flow__edge-textwrapper", className]);
	(0, import_react.useEffect)(function() {
		if (edgeRef.current) {
			var textBbox = edgeRef.current.getBBox();
			setEdgeTextBbox({
				x: textBbox.x,
				y: textBbox.y,
				width: textBbox.width,
				height: textBbox.height
			});
		}
	}, [label]);
	if (typeof label === "undefined" || !label) return null;
	return /* @__PURE__ */ import_react.createElement("g", _objectSpread$c({
		transform: "translate(".concat(x - edgeTextBbox.width / 2, " ").concat(y - edgeTextBbox.height / 2, ")"),
		className: edgeTextClasses
	}, rest), labelShowBg && /* @__PURE__ */ import_react.createElement("rect", {
		width: edgeTextBbox.width + 2 * labelBgPadding[0],
		x: -labelBgPadding[0],
		y: -labelBgPadding[1],
		height: edgeTextBbox.height + 2 * labelBgPadding[1],
		className: "react-flow__edge-textbg",
		style: labelBgStyle,
		rx: labelBgBorderRadius,
		ry: labelBgBorderRadius
	}), /* @__PURE__ */ import_react.createElement("text", {
		className: "react-flow__edge-text",
		y: edgeTextBbox.height / 2,
		dy: "0.3em",
		ref: edgeRef,
		style: labelStyle
	}, label), children);
});
var BaseEdge = (function(_ref) {
	var path = _ref.path, centerX = _ref.centerX, centerY = _ref.centerY, label = _ref.label, labelStyle = _ref.labelStyle, labelShowBg = _ref.labelShowBg, labelBgStyle = _ref.labelBgStyle, labelBgPadding = _ref.labelBgPadding, labelBgBorderRadius = _ref.labelBgBorderRadius, style = _ref.style, markerEnd = _ref.markerEnd, markerStart = _ref.markerStart;
	var text = label ? /* @__PURE__ */ import_react.createElement(EdgeText$1, {
		x: centerX,
		y: centerY,
		label,
		labelStyle,
		labelShowBg,
		labelBgStyle,
		labelBgPadding,
		labelBgBorderRadius
	}) : null;
	return /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, /* @__PURE__ */ import_react.createElement("path", {
		style,
		d: path,
		className: "react-flow__edge-path",
		markerEnd,
		markerStart
	}), text);
});
function getControl(_ref) {
	var pos = _ref.pos, x1 = _ref.x1, y1 = _ref.y1, x2 = _ref.x2, y2 = _ref.y2;
	var ctX, ctY;
	switch (pos) {
		case Position.Left:
		case Position.Right:
			ctX = .5 * (x1 + x2);
			ctY = y1;
			break;
		case Position.Top:
		case Position.Bottom:
			ctX = x1;
			ctY = .5 * (y1 + y2);
			break;
	}
	return [ctX, ctY];
}
function getSimpleBezierPath(_ref2) {
	var sourceX = _ref2.sourceX, sourceY = _ref2.sourceY, _ref2$sourcePosition = _ref2.sourcePosition, sourcePosition = _ref2$sourcePosition === void 0 ? Position.Bottom : _ref2$sourcePosition, targetX = _ref2.targetX, targetY = _ref2.targetY, _ref2$targetPosition = _ref2.targetPosition, targetPosition = _ref2$targetPosition === void 0 ? Position.Top : _ref2$targetPosition;
	var _getControl2 = _slicedToArray(getControl({
		pos: sourcePosition,
		x1: sourceX,
		y1: sourceY,
		x2: targetX,
		y2: targetY
	}), 2), sourceControlX = _getControl2[0], sourceControlY = _getControl2[1];
	var _getControl4 = _slicedToArray(getControl({
		pos: targetPosition,
		x1: targetX,
		y1: targetY,
		x2: sourceX,
		y2: sourceY
	}), 2), targetControlX = _getControl4[0], targetControlY = _getControl4[1];
	return "M".concat(sourceX, ",").concat(sourceY, " C").concat(sourceControlX, ",").concat(sourceControlY, " ").concat(targetControlX, ",").concat(targetControlY, " ").concat(targetX, ",").concat(targetY);
}
function getSimpleBezierCenter(_ref3) {
	var sourceX = _ref3.sourceX, sourceY = _ref3.sourceY, _ref3$sourcePosition = _ref3.sourcePosition, sourcePosition = _ref3$sourcePosition === void 0 ? Position.Bottom : _ref3$sourcePosition, targetX = _ref3.targetX, targetY = _ref3.targetY, _ref3$targetPosition = _ref3.targetPosition, targetPosition = _ref3$targetPosition === void 0 ? Position.Top : _ref3$targetPosition;
	var _getControl6 = _slicedToArray(getControl({
		pos: sourcePosition,
		x1: sourceX,
		y1: sourceY,
		x2: targetX,
		y2: targetY
	}), 2), sourceControlX = _getControl6[0], sourceControlY = _getControl6[1];
	var _getControl8 = _slicedToArray(getControl({
		pos: targetPosition,
		x1: targetX,
		y1: targetY,
		x2: sourceX,
		y2: sourceY
	}), 2), targetControlX = _getControl8[0], targetControlY = _getControl8[1];
	var centerX = sourceX * .125 + sourceControlX * .375 + targetControlX * .375 + targetX * .125;
	var centerY = sourceY * .125 + sourceControlY * .375 + targetControlY * .375 + targetY * .125;
	return [
		centerX,
		centerY,
		Math.abs(centerX - sourceX),
		Math.abs(centerY - sourceY)
	];
}
var SimpleBezierEdge = /* @__PURE__ */ (0, import_react.memo)(function(_ref4) {
	var sourceX = _ref4.sourceX, sourceY = _ref4.sourceY, targetX = _ref4.targetX, targetY = _ref4.targetY, _ref4$sourcePosition = _ref4.sourcePosition, sourcePosition = _ref4$sourcePosition === void 0 ? Position.Bottom : _ref4$sourcePosition, _ref4$targetPosition = _ref4.targetPosition, targetPosition = _ref4$targetPosition === void 0 ? Position.Top : _ref4$targetPosition, label = _ref4.label, labelStyle = _ref4.labelStyle, labelShowBg = _ref4.labelShowBg, labelBgStyle = _ref4.labelBgStyle, labelBgPadding = _ref4.labelBgPadding, labelBgBorderRadius = _ref4.labelBgBorderRadius, style = _ref4.style, markerEnd = _ref4.markerEnd, markerStart = _ref4.markerStart;
	var params = {
		sourceX,
		sourceY,
		sourcePosition,
		targetX,
		targetY,
		targetPosition
	};
	var path = getSimpleBezierPath(params);
	var _getSimpleBezierCente2 = _slicedToArray(getSimpleBezierCenter(params), 2), centerX = _getSimpleBezierCente2[0], centerY = _getSimpleBezierCente2[1];
	return /* @__PURE__ */ import_react.createElement(BaseEdge, {
		path,
		centerX,
		centerY,
		label,
		labelStyle,
		labelShowBg,
		labelBgStyle,
		labelBgPadding,
		labelBgBorderRadius,
		style,
		markerEnd,
		markerStart
	});
});
function ownKeys$b(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$b(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$b(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$b(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var getMarkerEnd = function getMarkerEnd(markerType, markerEndId) {
	if (typeof markerEndId !== "undefined" && markerEndId) return "url(#".concat(markerEndId, ")");
	return typeof markerType !== "undefined" ? "url(#react-flow__".concat(markerType, ")") : "none";
};
var LeftOrRight = [Position.Left, Position.Right];
var getCenter = function getCenter(_ref) {
	var sourceX = _ref.sourceX, sourceY = _ref.sourceY, targetX = _ref.targetX, targetY = _ref.targetY, _ref$sourcePosition = _ref.sourcePosition, sourcePosition = _ref$sourcePosition === void 0 ? Position.Bottom : _ref$sourcePosition, _ref$targetPosition = _ref.targetPosition, targetPosition = _ref$targetPosition === void 0 ? Position.Top : _ref$targetPosition;
	var sourceIsLeftOrRight = LeftOrRight.includes(sourcePosition);
	var targetIsLeftOrRight = LeftOrRight.includes(targetPosition);
	if (sourceIsLeftOrRight && !targetIsLeftOrRight || targetIsLeftOrRight && !sourceIsLeftOrRight) {
		var _xOffset = sourceIsLeftOrRight ? Math.abs(targetX - sourceX) : 0;
		var _centerX = sourceX > targetX ? sourceX - _xOffset : sourceX + _xOffset;
		var _yOffset = sourceIsLeftOrRight ? 0 : Math.abs(targetY - sourceY);
		return [
			_centerX,
			sourceY < targetY ? sourceY + _yOffset : sourceY - _yOffset,
			_xOffset,
			_yOffset
		];
	}
	var xOffset = Math.abs(targetX - sourceX) / 2;
	var centerX = targetX < sourceX ? targetX + xOffset : targetX - xOffset;
	var yOffset = Math.abs(targetY - sourceY) / 2;
	return [
		centerX,
		targetY < sourceY ? targetY + yOffset : targetY - yOffset,
		xOffset,
		yOffset
	];
};
function getMouseHandler(id, getState, handler) {
	return handler === void 0 ? handler : function(event) {
		handler(event, _objectSpread$b({}, getState().edges.find(function(e) {
			return e.id === id;
		})));
	};
}
var bottomLeftCorner = function bottomLeftCorner(x, y, size) {
	return "L ".concat(x, ",").concat(y - size, "Q ").concat(x, ",").concat(y, " ").concat(x + size, ",").concat(y);
};
var leftBottomCorner = function leftBottomCorner(x, y, size) {
	return "L ".concat(x + size, ",").concat(y, "Q ").concat(x, ",").concat(y, " ").concat(x, ",").concat(y - size);
};
var bottomRightCorner = function bottomRightCorner(x, y, size) {
	return "L ".concat(x, ",").concat(y - size, "Q ").concat(x, ",").concat(y, " ").concat(x - size, ",").concat(y);
};
var rightBottomCorner = function rightBottomCorner(x, y, size) {
	return "L ".concat(x - size, ",").concat(y, "Q ").concat(x, ",").concat(y, " ").concat(x, ",").concat(y - size);
};
var leftTopCorner = function leftTopCorner(x, y, size) {
	return "L ".concat(x + size, ",").concat(y, "Q ").concat(x, ",").concat(y, " ").concat(x, ",").concat(y + size);
};
var topLeftCorner = function topLeftCorner(x, y, size) {
	return "L ".concat(x, ",").concat(y + size, "Q ").concat(x, ",").concat(y, " ").concat(x + size, ",").concat(y);
};
var topRightCorner = function topRightCorner(x, y, size) {
	return "L ".concat(x, ",").concat(y + size, "Q ").concat(x, ",").concat(y, " ").concat(x - size, ",").concat(y);
};
var rightTopCorner = function rightTopCorner(x, y, size) {
	return "L ".concat(x - size, ",").concat(y, "Q ").concat(x, ",").concat(y, " ").concat(x, ",").concat(y + size);
};
function getSmoothStepPath(_ref) {
	var sourceX = _ref.sourceX, sourceY = _ref.sourceY, _ref$sourcePosition = _ref.sourcePosition, sourcePosition = _ref$sourcePosition === void 0 ? Position.Bottom : _ref$sourcePosition, targetX = _ref.targetX, targetY = _ref.targetY, _ref$targetPosition = _ref.targetPosition, targetPosition = _ref$targetPosition === void 0 ? Position.Top : _ref$targetPosition, _ref$borderRadius = _ref.borderRadius, borderRadius = _ref$borderRadius === void 0 ? 5 : _ref$borderRadius, centerX = _ref.centerX, centerY = _ref.centerY;
	var _getCenter2 = _slicedToArray(getCenter({
		sourceX,
		sourceY,
		targetX,
		targetY
	}), 4), _centerX = _getCenter2[0], _centerY = _getCenter2[1], offsetX = _getCenter2[2], offsetY = _getCenter2[3];
	var cornerWidth = Math.min(borderRadius, Math.abs(targetX - sourceX));
	var cornerHeight = Math.min(borderRadius, Math.abs(targetY - sourceY));
	var cornerSize = Math.min(cornerWidth, cornerHeight, offsetX, offsetY);
	var leftAndRight = [Position.Left, Position.Right];
	var cX = typeof centerX !== "undefined" ? centerX : _centerX;
	var cY = typeof centerY !== "undefined" ? centerY : _centerY;
	var firstCornerPath = null;
	var secondCornerPath = null;
	if (sourceX <= targetX) {
		firstCornerPath = sourceY <= targetY ? bottomLeftCorner(sourceX, cY, cornerSize) : topLeftCorner(sourceX, cY, cornerSize);
		secondCornerPath = sourceY <= targetY ? rightTopCorner(targetX, cY, cornerSize) : rightBottomCorner(targetX, cY, cornerSize);
	} else {
		firstCornerPath = sourceY < targetY ? bottomRightCorner(sourceX, cY, cornerSize) : topRightCorner(sourceX, cY, cornerSize);
		secondCornerPath = sourceY < targetY ? leftTopCorner(targetX, cY, cornerSize) : leftBottomCorner(targetX, cY, cornerSize);
	}
	if (leftAndRight.includes(sourcePosition) && leftAndRight.includes(targetPosition)) {
		if (sourceX <= targetX) {
			firstCornerPath = sourceY <= targetY ? rightTopCorner(cX, sourceY, cornerSize) : rightBottomCorner(cX, sourceY, cornerSize);
			secondCornerPath = sourceY <= targetY ? bottomLeftCorner(cX, targetY, cornerSize) : topLeftCorner(cX, targetY, cornerSize);
		} else if (sourcePosition === Position.Right && targetPosition === Position.Left || sourcePosition === Position.Left && targetPosition === Position.Right || sourcePosition === Position.Left && targetPosition === Position.Left) {
			firstCornerPath = sourceY <= targetY ? leftTopCorner(cX, sourceY, cornerSize) : leftBottomCorner(cX, sourceY, cornerSize);
			secondCornerPath = sourceY <= targetY ? bottomRightCorner(cX, targetY, cornerSize) : topRightCorner(cX, targetY, cornerSize);
		}
	} else if (leftAndRight.includes(sourcePosition) && !leftAndRight.includes(targetPosition)) {
		if (sourceX <= targetX) firstCornerPath = sourceY <= targetY ? rightTopCorner(targetX, sourceY, cornerSize) : rightBottomCorner(targetX, sourceY, cornerSize);
		else firstCornerPath = sourceY <= targetY ? leftTopCorner(targetX, sourceY, cornerSize) : leftBottomCorner(targetX, sourceY, cornerSize);
		secondCornerPath = "";
	} else if (!leftAndRight.includes(sourcePosition) && leftAndRight.includes(targetPosition)) {
		if (sourceX <= targetX) firstCornerPath = sourceY <= targetY ? bottomLeftCorner(sourceX, targetY, cornerSize) : topLeftCorner(sourceX, targetY, cornerSize);
		else firstCornerPath = sourceY <= targetY ? bottomRightCorner(sourceX, targetY, cornerSize) : topRightCorner(sourceX, targetY, cornerSize);
		secondCornerPath = "";
	}
	return "M ".concat(sourceX, ",").concat(sourceY).concat(firstCornerPath).concat(secondCornerPath, "L ").concat(targetX, ",").concat(targetY);
}
var SmoothStepEdge = /* @__PURE__ */ (0, import_react.memo)(function(_ref2) {
	var sourceX = _ref2.sourceX, sourceY = _ref2.sourceY, targetX = _ref2.targetX, targetY = _ref2.targetY, label = _ref2.label, labelStyle = _ref2.labelStyle, labelShowBg = _ref2.labelShowBg, labelBgStyle = _ref2.labelBgStyle, labelBgPadding = _ref2.labelBgPadding, labelBgBorderRadius = _ref2.labelBgBorderRadius, style = _ref2.style, _ref2$sourcePosition = _ref2.sourcePosition, sourcePosition = _ref2$sourcePosition === void 0 ? Position.Bottom : _ref2$sourcePosition, _ref2$targetPosition = _ref2.targetPosition, targetPosition = _ref2$targetPosition === void 0 ? Position.Top : _ref2$targetPosition, markerEnd = _ref2.markerEnd, markerStart = _ref2.markerStart, _ref2$borderRadius = _ref2.borderRadius, borderRadius = _ref2$borderRadius === void 0 ? 5 : _ref2$borderRadius;
	var _getCenter4 = _slicedToArray(getCenter({
		sourceX,
		sourceY,
		targetX,
		targetY,
		sourcePosition,
		targetPosition
	}), 2), centerX = _getCenter4[0], centerY = _getCenter4[1];
	var path = getSmoothStepPath({
		sourceX,
		sourceY,
		sourcePosition,
		targetX,
		targetY,
		targetPosition,
		borderRadius
	});
	return /* @__PURE__ */ import_react.createElement(BaseEdge, {
		path,
		centerX,
		centerY,
		label,
		labelStyle,
		labelShowBg,
		labelBgStyle,
		labelBgPadding,
		labelBgBorderRadius,
		style,
		markerEnd,
		markerStart
	});
});
function ownKeys$a(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$a(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$a(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$a(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var StepEdge = /* @__PURE__ */ (0, import_react.memo)(function(props) {
	return /* @__PURE__ */ import_react.createElement(SmoothStepEdge, _objectSpread$a(_objectSpread$a({}, props), {}, { borderRadius: 0 }));
});
var StraightEdge = /* @__PURE__ */ (0, import_react.memo)(function(_ref) {
	var sourceX = _ref.sourceX, sourceY = _ref.sourceY, targetX = _ref.targetX, targetY = _ref.targetY, label = _ref.label, labelStyle = _ref.labelStyle, labelShowBg = _ref.labelShowBg, labelBgStyle = _ref.labelBgStyle, labelBgPadding = _ref.labelBgPadding, labelBgBorderRadius = _ref.labelBgBorderRadius, style = _ref.style, markerEnd = _ref.markerEnd, markerStart = _ref.markerStart;
	var yOffset = Math.abs(targetY - sourceY) / 2;
	var centerY = targetY < sourceY ? targetY + yOffset : targetY - yOffset;
	var xOffset = Math.abs(targetX - sourceX) / 2;
	var centerX = targetX < sourceX ? targetX + xOffset : targetX - xOffset;
	var path = "M ".concat(sourceX, ",").concat(sourceY, "L ").concat(targetX, ",").concat(targetY);
	return /* @__PURE__ */ import_react.createElement(BaseEdge, {
		path,
		centerX,
		centerY,
		label,
		labelStyle,
		labelShowBg,
		labelBgStyle,
		labelBgPadding,
		labelBgBorderRadius,
		style,
		markerEnd,
		markerStart
	});
});
function calculateControlOffset(distance, curvature) {
	if (distance >= 0) return .5 * distance;
	else return curvature * 25 * Math.sqrt(-distance);
}
function getControlWithCurvature(_ref) {
	var pos = _ref.pos, x1 = _ref.x1, y1 = _ref.y1, x2 = _ref.x2, y2 = _ref.y2, c = _ref.c;
	var ctX, ctY;
	switch (pos) {
		case Position.Left:
			ctX = x1 - calculateControlOffset(x1 - x2, c);
			ctY = y1;
			break;
		case Position.Right:
			ctX = x1 + calculateControlOffset(x2 - x1, c);
			ctY = y1;
			break;
		case Position.Top:
			ctX = x1;
			ctY = y1 - calculateControlOffset(y1 - y2, c);
			break;
		case Position.Bottom:
			ctX = x1;
			ctY = y1 + calculateControlOffset(y2 - y1, c);
			break;
	}
	return [ctX, ctY];
}
function getBezierPath(_ref2) {
	var sourceX = _ref2.sourceX, sourceY = _ref2.sourceY, _ref2$sourcePosition = _ref2.sourcePosition, sourcePosition = _ref2$sourcePosition === void 0 ? Position.Bottom : _ref2$sourcePosition, targetX = _ref2.targetX, targetY = _ref2.targetY, _ref2$targetPosition = _ref2.targetPosition, targetPosition = _ref2$targetPosition === void 0 ? Position.Top : _ref2$targetPosition, _ref2$curvature = _ref2.curvature, curvature = _ref2$curvature === void 0 ? .25 : _ref2$curvature;
	var _getControlWithCurvat2 = _slicedToArray(getControlWithCurvature({
		pos: sourcePosition,
		x1: sourceX,
		y1: sourceY,
		x2: targetX,
		y2: targetY,
		c: curvature
	}), 2), sourceControlX = _getControlWithCurvat2[0], sourceControlY = _getControlWithCurvat2[1];
	var _getControlWithCurvat4 = _slicedToArray(getControlWithCurvature({
		pos: targetPosition,
		x1: targetX,
		y1: targetY,
		x2: sourceX,
		y2: sourceY,
		c: curvature
	}), 2), targetControlX = _getControlWithCurvat4[0], targetControlY = _getControlWithCurvat4[1];
	return "M".concat(sourceX, ",").concat(sourceY, " C").concat(sourceControlX, ",").concat(sourceControlY, " ").concat(targetControlX, ",").concat(targetControlY, " ").concat(targetX, ",").concat(targetY);
}
function getBezierCenter(_ref3) {
	var sourceX = _ref3.sourceX, sourceY = _ref3.sourceY, _ref3$sourcePosition = _ref3.sourcePosition, sourcePosition = _ref3$sourcePosition === void 0 ? Position.Bottom : _ref3$sourcePosition, targetX = _ref3.targetX, targetY = _ref3.targetY, _ref3$targetPosition = _ref3.targetPosition, targetPosition = _ref3$targetPosition === void 0 ? Position.Top : _ref3$targetPosition, _ref3$curvature = _ref3.curvature, curvature = _ref3$curvature === void 0 ? .25 : _ref3$curvature;
	var _getControlWithCurvat6 = _slicedToArray(getControlWithCurvature({
		pos: sourcePosition,
		x1: sourceX,
		y1: sourceY,
		x2: targetX,
		y2: targetY,
		c: curvature
	}), 2), sourceControlX = _getControlWithCurvat6[0], sourceControlY = _getControlWithCurvat6[1];
	var _getControlWithCurvat8 = _slicedToArray(getControlWithCurvature({
		pos: targetPosition,
		x1: targetX,
		y1: targetY,
		x2: sourceX,
		y2: sourceY,
		c: curvature
	}), 2), targetControlX = _getControlWithCurvat8[0], targetControlY = _getControlWithCurvat8[1];
	var centerX = sourceX * .125 + sourceControlX * .375 + targetControlX * .375 + targetX * .125;
	var centerY = sourceY * .125 + sourceControlY * .375 + targetControlY * .375 + targetY * .125;
	return [
		centerX,
		centerY,
		Math.abs(centerX - sourceX),
		Math.abs(centerY - sourceY)
	];
}
var BezierEdge = /* @__PURE__ */ (0, import_react.memo)(function(_ref4) {
	var sourceX = _ref4.sourceX, sourceY = _ref4.sourceY, targetX = _ref4.targetX, targetY = _ref4.targetY, _ref4$sourcePosition = _ref4.sourcePosition, sourcePosition = _ref4$sourcePosition === void 0 ? Position.Bottom : _ref4$sourcePosition, _ref4$targetPosition = _ref4.targetPosition, targetPosition = _ref4$targetPosition === void 0 ? Position.Top : _ref4$targetPosition, label = _ref4.label, labelStyle = _ref4.labelStyle, labelShowBg = _ref4.labelShowBg, labelBgStyle = _ref4.labelBgStyle, labelBgPadding = _ref4.labelBgPadding, labelBgBorderRadius = _ref4.labelBgBorderRadius, style = _ref4.style, markerEnd = _ref4.markerEnd, markerStart = _ref4.markerStart;
	var params = {
		sourceX,
		sourceY,
		sourcePosition,
		targetX,
		targetY,
		targetPosition,
		curvature: _ref4.curvature
	};
	var path = getBezierPath(params);
	var _getBezierCenter2 = _slicedToArray(getBezierCenter(params), 2), centerX = _getBezierCenter2[0], centerY = _getBezierCenter2[1];
	return /* @__PURE__ */ import_react.createElement(BaseEdge, {
		path,
		centerX,
		centerY,
		label,
		labelStyle,
		labelShowBg,
		labelBgStyle,
		labelBgPadding,
		labelBgBorderRadius,
		style,
		markerEnd,
		markerStart
	});
});
var NodeIdContext = /* @__PURE__ */ (0, import_react.createContext)(null);
var Provider = NodeIdContext.Provider;
NodeIdContext.Consumer;
function checkElementBelowIsValid(event, connectionMode, isTarget, nodeId, handleId, isValidConnection, doc) {
	var elementBelow = doc.elementFromPoint(event.clientX, event.clientY);
	var elementBelowIsTarget = (elementBelow === null || elementBelow === void 0 ? void 0 : elementBelow.classList.contains("target")) || false;
	var elementBelowIsSource = (elementBelow === null || elementBelow === void 0 ? void 0 : elementBelow.classList.contains("source")) || false;
	var result = {
		elementBelow,
		isValid: false,
		connection: {
			source: null,
			target: null,
			sourceHandle: null,
			targetHandle: null
		},
		isHoveringHandle: false
	};
	if (elementBelow && (elementBelowIsTarget || elementBelowIsSource)) {
		result.isHoveringHandle = true;
		var elementBelowNodeId = elementBelow.getAttribute("data-nodeid");
		var elementBelowHandleId = elementBelow.getAttribute("data-handleid");
		var connection = isTarget ? {
			source: elementBelowNodeId,
			sourceHandle: elementBelowHandleId,
			target: nodeId,
			targetHandle: handleId
		} : {
			source: nodeId,
			sourceHandle: handleId,
			target: elementBelowNodeId,
			targetHandle: elementBelowHandleId
		};
		result.connection = connection;
		if (connectionMode === ConnectionMode.Strict ? isTarget && elementBelowIsSource || !isTarget && elementBelowIsTarget : true) result.isValid = isValidConnection(connection);
	}
	return result;
}
function resetRecentHandle(hoveredHandle) {
	hoveredHandle === null || hoveredHandle === void 0 || hoveredHandle.classList.remove("react-flow__handle-valid");
	hoveredHandle === null || hoveredHandle === void 0 || hoveredHandle.classList.remove("react-flow__handle-connecting");
}
function handleMouseDown(_ref) {
	var event = _ref.event, handleId = _ref.handleId, nodeId = _ref.nodeId, onConnect = _ref.onConnect, isTarget = _ref.isTarget, getState = _ref.getState, setState = _ref.setState, isValidConnection = _ref.isValidConnection, elementEdgeUpdaterType = _ref.elementEdgeUpdaterType, onEdgeUpdateEnd = _ref.onEdgeUpdateEnd;
	var reactFlowNode = event.target.closest(".react-flow");
	var doc = getHostForElement(event.target);
	if (!doc) return;
	var elementBelow = doc.elementFromPoint(event.clientX, event.clientY);
	var elementBelowIsTarget = elementBelow === null || elementBelow === void 0 ? void 0 : elementBelow.classList.contains("target");
	var elementBelowIsSource = elementBelow === null || elementBelow === void 0 ? void 0 : elementBelow.classList.contains("source");
	if (!reactFlowNode || !elementBelowIsTarget && !elementBelowIsSource && !elementEdgeUpdaterType) return;
	var _getState = getState(), onConnectStart = _getState.onConnectStart, connectionMode = _getState.connectionMode;
	var handleType = elementEdgeUpdaterType ? elementEdgeUpdaterType : elementBelowIsTarget ? "target" : "source";
	var containerBounds = reactFlowNode.getBoundingClientRect();
	var recentHoveredHandle;
	setState({
		connectionPosition: {
			x: event.clientX - containerBounds.left,
			y: event.clientY - containerBounds.top
		},
		connectionNodeId: nodeId,
		connectionHandleId: handleId,
		connectionHandleType: handleType
	});
	onConnectStart === null || onConnectStart === void 0 || onConnectStart(event, {
		nodeId,
		handleId,
		handleType
	});
	function onMouseMove(event) {
		setState({ connectionPosition: {
			x: event.clientX - containerBounds.left,
			y: event.clientY - containerBounds.top
		} });
		var _checkElementBelowIsV = checkElementBelowIsValid(event, connectionMode, isTarget, nodeId, handleId, isValidConnection, doc), connection = _checkElementBelowIsV.connection, elementBelow = _checkElementBelowIsV.elementBelow, isValid = _checkElementBelowIsV.isValid;
		if (!_checkElementBelowIsV.isHoveringHandle) return resetRecentHandle(recentHoveredHandle);
		if (connection.source !== connection.target && elementBelow) {
			resetRecentHandle(recentHoveredHandle);
			recentHoveredHandle = elementBelow;
			elementBelow.classList.add("react-flow__handle-connecting");
			elementBelow.classList.toggle("react-flow__handle-valid", isValid);
		}
	}
	function onMouseUp(event) {
		var _getState2 = getState(), onConnectStop = _getState2.onConnectStop, onConnectEnd = _getState2.onConnectEnd;
		var _checkElementBelowIsV2 = checkElementBelowIsValid(event, connectionMode, isTarget, nodeId, handleId, isValidConnection, doc), connection = _checkElementBelowIsV2.connection, isValid = _checkElementBelowIsV2.isValid;
		onConnectStop === null || onConnectStop === void 0 || onConnectStop(event);
		if (isValid) onConnect === null || onConnect === void 0 || onConnect(connection);
		onConnectEnd === null || onConnectEnd === void 0 || onConnectEnd(event);
		if (elementEdgeUpdaterType && onEdgeUpdateEnd) onEdgeUpdateEnd(event);
		resetRecentHandle(recentHoveredHandle);
		setState({
			connectionNodeId: null,
			connectionHandleId: null,
			connectionHandleType: null
		});
		doc.removeEventListener("mousemove", onMouseMove);
		doc.removeEventListener("mouseup", onMouseUp);
	}
	doc.addEventListener("mousemove", onMouseMove);
	doc.addEventListener("mouseup", onMouseUp);
}
var _excluded$1 = [
	"type",
	"position",
	"isValidConnection",
	"isConnectable",
	"id",
	"onConnect",
	"children",
	"className",
	"onMouseDown"
];
function ownKeys$9(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$9(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$9(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$9(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var alwaysValid = function alwaysValid() {
	return true;
};
var selector$a = function selector(s) {
	return {
		connectionStartHandle: s.connectionStartHandle,
		connectOnClick: s.connectOnClick
	};
};
var Handle = /* @__PURE__ */ (0, import_react.forwardRef)(function(_ref, ref) {
	var _ref$type = _ref.type, type = _ref$type === void 0 ? "source" : _ref$type, _ref$position = _ref.position, position = _ref$position === void 0 ? Position.Top : _ref$position, _ref$isValidConnectio = _ref.isValidConnection, isValidConnection = _ref$isValidConnectio === void 0 ? alwaysValid : _ref$isValidConnectio, _ref$isConnectable = _ref.isConnectable, isConnectable = _ref$isConnectable === void 0 ? true : _ref$isConnectable, id = _ref.id, onConnect = _ref.onConnect, children = _ref.children, className = _ref.className, onMouseDown = _ref.onMouseDown, rest = _objectWithoutProperties(_ref, _excluded$1);
	var store = useStoreApi();
	var nodeId = (0, import_react.useContext)(NodeIdContext);
	var _useStore = useStore(selector$a, shallow), connectionStartHandle = _useStore.connectionStartHandle, connectOnClick = _useStore.connectOnClick;
	var handleId = id || null;
	var isTarget = type === "target";
	var onConnectExtended = function onConnectExtended(params) {
		var _store$getState = store.getState(), defaultEdgeOptions = _store$getState.defaultEdgeOptions, onConnectAction = _store$getState.onConnect, hasDefaultEdges = _store$getState.hasDefaultEdges;
		var edgeParams = _objectSpread$9(_objectSpread$9({}, defaultEdgeOptions), params);
		if (hasDefaultEdges) {
			var edges = store.getState().edges;
			store.setState({ edges: addEdge(edgeParams, edges) });
		}
		onConnectAction === null || onConnectAction === void 0 || onConnectAction(edgeParams);
		onConnect === null || onConnect === void 0 || onConnect(edgeParams);
	};
	var onMouseDownHandler = function onMouseDownHandler(event) {
		if (event.button === 0) handleMouseDown({
			event,
			handleId,
			nodeId,
			onConnect: onConnectExtended,
			isTarget,
			getState: store.getState,
			setState: store.setState,
			isValidConnection
		});
		onMouseDown === null || onMouseDown === void 0 || onMouseDown(event);
	};
	var onClick = function onClick(event) {
		var _store$getState3 = store.getState(), onClickConnectStart = _store$getState3.onClickConnectStart, onClickConnectStop = _store$getState3.onClickConnectStop, onClickConnectEnd = _store$getState3.onClickConnectEnd, connectionMode = _store$getState3.connectionMode;
		if (!connectionStartHandle) {
			onClickConnectStart === null || onClickConnectStart === void 0 || onClickConnectStart(event, {
				nodeId,
				handleId,
				handleType: type
			});
			store.setState({ connectionStartHandle: {
				nodeId,
				type,
				handleId
			} });
			return;
		}
		var doc = getHostForElement(event.target);
		var _checkElementBelowIsV = checkElementBelowIsValid(event, connectionMode, connectionStartHandle.type === "target", connectionStartHandle.nodeId, connectionStartHandle.handleId || null, isValidConnection, doc), connection = _checkElementBelowIsV.connection, isValid = _checkElementBelowIsV.isValid;
		onClickConnectStop === null || onClickConnectStop === void 0 || onClickConnectStop(event);
		if (isValid) onConnectExtended(connection);
		onClickConnectEnd === null || onClickConnectEnd === void 0 || onClickConnectEnd(event);
		store.setState({ connectionStartHandle: null });
	};
	return /* @__PURE__ */ import_react.createElement("div", _objectSpread$9({
		"data-handleid": handleId,
		"data-nodeid": nodeId,
		"data-handlepos": position,
		className: cc([
			"react-flow__handle",
			"react-flow__handle-".concat(position),
			"nodrag",
			className,
			{
				source: !isTarget,
				target: isTarget,
				connectable: isConnectable,
				connecting: (connectionStartHandle === null || connectionStartHandle === void 0 ? void 0 : connectionStartHandle.nodeId) === nodeId && (connectionStartHandle === null || connectionStartHandle === void 0 ? void 0 : connectionStartHandle.handleId) === handleId && (connectionStartHandle === null || connectionStartHandle === void 0 ? void 0 : connectionStartHandle.type) === type
			}
		]),
		onMouseDown: onMouseDownHandler,
		onClick: connectOnClick ? onClick : void 0,
		ref
	}, rest), children);
});
Handle.displayName = "Handle";
var Handle$1 = /* @__PURE__ */ (0, import_react.memo)(Handle);
var DefaultNode = function DefaultNode(_ref) {
	var data = _ref.data, isConnectable = _ref.isConnectable, _ref$targetPosition = _ref.targetPosition, targetPosition = _ref$targetPosition === void 0 ? Position.Top : _ref$targetPosition, _ref$sourcePosition = _ref.sourcePosition, sourcePosition = _ref$sourcePosition === void 0 ? Position.Bottom : _ref$sourcePosition;
	return /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, /* @__PURE__ */ import_react.createElement(Handle$1, {
		type: "target",
		position: targetPosition,
		isConnectable
	}), data === null || data === void 0 ? void 0 : data.label, /* @__PURE__ */ import_react.createElement(Handle$1, {
		type: "source",
		position: sourcePosition,
		isConnectable
	}));
};
DefaultNode.displayName = "DefaultNode";
var DefaultNode$1 = /* @__PURE__ */ (0, import_react.memo)(DefaultNode);
var InputNode = function InputNode(_ref) {
	var data = _ref.data, isConnectable = _ref.isConnectable, _ref$sourcePosition = _ref.sourcePosition, sourcePosition = _ref$sourcePosition === void 0 ? Position.Bottom : _ref$sourcePosition;
	return /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, data === null || data === void 0 ? void 0 : data.label, /* @__PURE__ */ import_react.createElement(Handle$1, {
		type: "source",
		position: sourcePosition,
		isConnectable
	}));
};
InputNode.displayName = "InputNode";
var InputNode$1 = /* @__PURE__ */ (0, import_react.memo)(InputNode);
var OutputNode = function OutputNode(_ref) {
	var data = _ref.data, isConnectable = _ref.isConnectable, _ref$targetPosition = _ref.targetPosition, targetPosition = _ref$targetPosition === void 0 ? Position.Top : _ref$targetPosition;
	return /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, /* @__PURE__ */ import_react.createElement(Handle$1, {
		type: "target",
		position: targetPosition,
		isConnectable
	}), data === null || data === void 0 ? void 0 : data.label);
};
OutputNode.displayName = "OutputNode";
var OutputNode$1 = /* @__PURE__ */ (0, import_react.memo)(OutputNode);
var selector$9 = function selector(s) {
	return {
		selectedNodes: Array.from(s.nodeInternals.values()).filter(function(n) {
			return n.selected;
		}),
		selectedEdges: s.edges.filter(function(e) {
			return e.selected;
		})
	};
};
var areEqual = function areEqual(objA, objB) {
	var selectedNodeIdsA = objA.selectedNodes.map(function(n) {
		return n.id;
	});
	var selectedNodeIdsB = objB.selectedNodes.map(function(n) {
		return n.id;
	});
	var selectedEdgeIdsA = objA.selectedEdges.map(function(e) {
		return e.id;
	});
	var selectedEdgeIdsB = objB.selectedEdges.map(function(e) {
		return e.id;
	});
	return shallow(selectedNodeIdsA, selectedNodeIdsB) && shallow(selectedEdgeIdsA, selectedEdgeIdsB);
};
function SelectionListener(_ref) {
	var onSelectionChange = _ref.onSelectionChange;
	var _useStore = useStore(selector$9, areEqual), selectedNodes = _useStore.selectedNodes, selectedEdges = _useStore.selectedEdges;
	(0, import_react.useEffect)(function() {
		onSelectionChange({
			nodes: selectedNodes,
			edges: selectedEdges
		});
	}, [selectedNodes, selectedEdges]);
	return null;
}
var SelectionListener$1 = /* @__PURE__ */ (0, import_react.memo)(SelectionListener);
var selector$8 = function selector(s) {
	return {
		setNodes: s.setNodes,
		setEdges: s.setEdges,
		setDefaultNodesAndEdges: s.setDefaultNodesAndEdges,
		setMinZoom: s.setMinZoom,
		setMaxZoom: s.setMaxZoom,
		setTranslateExtent: s.setTranslateExtent,
		setNodeExtent: s.setNodeExtent,
		reset: s.reset
	};
};
function useStoreUpdater(value, setStoreState) {
	(0, import_react.useEffect)(function() {
		if (typeof value !== "undefined") setStoreState(value);
	}, [value]);
}
function useDirectStoreUpdater(key, value, setState) {
	(0, import_react.useEffect)(function() {
		if (typeof value !== "undefined") setState(_defineProperty({}, key, value));
	}, [value]);
}
var StoreUpdater = function StoreUpdater(_ref) {
	var nodes = _ref.nodes, edges = _ref.edges, defaultNodes = _ref.defaultNodes, defaultEdges = _ref.defaultEdges, onConnect = _ref.onConnect, onConnectStart = _ref.onConnectStart, onConnectStop = _ref.onConnectStop, onConnectEnd = _ref.onConnectEnd, onClickConnectStart = _ref.onClickConnectStart, onClickConnectStop = _ref.onClickConnectStop, onClickConnectEnd = _ref.onClickConnectEnd, nodesDraggable = _ref.nodesDraggable, nodesConnectable = _ref.nodesConnectable, minZoom = _ref.minZoom, maxZoom = _ref.maxZoom, nodeExtent = _ref.nodeExtent, onNodesChange = _ref.onNodesChange, onEdgesChange = _ref.onEdgesChange, elementsSelectable = _ref.elementsSelectable, connectionMode = _ref.connectionMode, snapGrid = _ref.snapGrid, snapToGrid = _ref.snapToGrid, translateExtent = _ref.translateExtent, connectOnClick = _ref.connectOnClick, defaultEdgeOptions = _ref.defaultEdgeOptions, fitView = _ref.fitView, fitViewOptions = _ref.fitViewOptions, onNodesDelete = _ref.onNodesDelete, onEdgesDelete = _ref.onEdgesDelete, onNodeDrag = _ref.onNodeDrag, onNodeDragStart = _ref.onNodeDragStart, onNodeDragStop = _ref.onNodeDragStop, onSelectionDrag = _ref.onSelectionDrag, onSelectionDragStart = _ref.onSelectionDragStart, onSelectionDragStop = _ref.onSelectionDragStop;
	var _useStore = useStore(selector$8, shallow), setNodes = _useStore.setNodes, setEdges = _useStore.setEdges, setDefaultNodesAndEdges = _useStore.setDefaultNodesAndEdges, setMinZoom = _useStore.setMinZoom, setMaxZoom = _useStore.setMaxZoom, setTranslateExtent = _useStore.setTranslateExtent, setNodeExtent = _useStore.setNodeExtent, reset = _useStore.reset;
	var store = useStoreApi();
	(0, import_react.useEffect)(function() {
		setDefaultNodesAndEdges(defaultNodes, defaultEdges);
		return function() {
			reset();
		};
	}, []);
	useDirectStoreUpdater("defaultEdgeOptions", defaultEdgeOptions, store.setState);
	useDirectStoreUpdater("connectionMode", connectionMode, store.setState);
	useDirectStoreUpdater("onConnect", onConnect, store.setState);
	useDirectStoreUpdater("onConnectStart", onConnectStart, store.setState);
	useDirectStoreUpdater("onConnectStop", onConnectStop, store.setState);
	useDirectStoreUpdater("onConnectEnd", onConnectEnd, store.setState);
	useDirectStoreUpdater("onClickConnectStart", onClickConnectStart, store.setState);
	useDirectStoreUpdater("onClickConnectStop", onClickConnectStop, store.setState);
	useDirectStoreUpdater("onClickConnectEnd", onClickConnectEnd, store.setState);
	useDirectStoreUpdater("nodesDraggable", nodesDraggable, store.setState);
	useDirectStoreUpdater("nodesConnectable", nodesConnectable, store.setState);
	useDirectStoreUpdater("elementsSelectable", elementsSelectable, store.setState);
	useDirectStoreUpdater("snapToGrid", snapToGrid, store.setState);
	useDirectStoreUpdater("snapGrid", snapGrid, store.setState);
	useDirectStoreUpdater("onNodesChange", onNodesChange, store.setState);
	useDirectStoreUpdater("onEdgesChange", onEdgesChange, store.setState);
	useDirectStoreUpdater("connectOnClick", connectOnClick, store.setState);
	useDirectStoreUpdater("fitViewOnInit", fitView, store.setState);
	useDirectStoreUpdater("fitViewOnInitOptions", fitViewOptions, store.setState);
	useDirectStoreUpdater("onNodesDelete", onNodesDelete, store.setState);
	useDirectStoreUpdater("onEdgesDelete", onEdgesDelete, store.setState);
	useDirectStoreUpdater("onNodeDrag", onNodeDrag, store.setState);
	useDirectStoreUpdater("onNodeDragStart", onNodeDragStart, store.setState);
	useDirectStoreUpdater("onNodeDragStop", onNodeDragStop, store.setState);
	useDirectStoreUpdater("onSelectionDrag", onSelectionDrag, store.setState);
	useDirectStoreUpdater("onSelectionDragStart", onSelectionDragStart, store.setState);
	useDirectStoreUpdater("onSelectionDragStop", onSelectionDragStop, store.setState);
	useStoreUpdater(nodes, setNodes);
	useStoreUpdater(edges, setEdges);
	useStoreUpdater(defaultNodes, setNodes);
	useStoreUpdater(defaultEdges, setEdges);
	useStoreUpdater(minZoom, setMinZoom);
	useStoreUpdater(maxZoom, setMaxZoom);
	useStoreUpdater(translateExtent, setTranslateExtent);
	useStoreUpdater(nodeExtent, setNodeExtent);
	return null;
};
var css = ".react-flow{height:100%;overflow:hidden;position:relative;width:100%}.react-flow__container{height:100%;left:0;position:absolute;top:0;width:100%}.react-flow__pane{z-index:1}.react-flow__viewport{pointer-events:none;transform-origin:0 0;z-index:2}.react-flow__renderer{z-index:4}.react-flow__selectionpane{z-index:5}.react-flow .react-flow__edges{overflow:visible;pointer-events:none}.react-flow .react-flow__connectionline{z-index:1001}.react-flow__edge{pointer-events:visibleStroke}.react-flow__edge.inactive{pointer-events:none}@-webkit-keyframes dashdraw{0%{stroke-dashoffset:10}}@keyframes dashdraw{0%{stroke-dashoffset:10}}.react-flow__edge-path{fill:none}.react-flow__edge-textwrapper{pointer-events:all}.react-flow__edge-text{pointer-events:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}.react-flow__connection{pointer-events:none}.react-flow__connection .animated{stroke-dasharray:5;-webkit-animation:dashdraw .5s linear infinite;animation:dashdraw .5s linear infinite}.react-flow__connection-path{fill:none}.react-flow__nodes{pointer-events:none;transform-origin:0 0}.react-flow__node{box-sizing:border-box;pointer-events:all;position:absolute;transform-origin:0 0;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}.react-flow__nodesselection{pointer-events:none;transform-origin:left top;z-index:3}.react-flow__nodesselection-rect{cursor:-webkit-grab;cursor:grab;pointer-events:all;position:absolute}.react-flow__handle{pointer-events:none;position:absolute}.react-flow__handle.connectable{pointer-events:all}.react-flow__handle-bottom{bottom:-4px;left:50%;top:auto;transform:translate(-50%)}.react-flow__handle-top{left:50%;top:-4px;transform:translate(-50%)}.react-flow__handle-left{left:-4px;top:50%;transform:translateY(-50%)}.react-flow__handle-right{right:-4px;top:50%;transform:translateY(-50%)}.react-flow__edgeupdater{cursor:move;pointer-events:all}.react-flow__controls{bottom:20px;left:15px;position:absolute;z-index:5}.react-flow__controls-button{border:none;height:24px;width:24px}.react-flow__controls-button svg{width:100%}.react-flow__minimap{bottom:20px;position:absolute;right:15px;z-index:5}.react-flow__attribution{background:hsla(0,0%,100%,.5);color:#999;font-size:10px;padding:2px 3px;position:absolute;z-index:1000}.react-flow__attribution a{color:#555;text-decoration:none}.react-flow__attribution.top{top:0}.react-flow__attribution.bottom{bottom:0}.react-flow__attribution.left{left:0}.react-flow__attribution.right{right:0}.react-flow__attribution.center{left:50%;transform:translateX(-50%)}";
var theme = ".react-flow__edge.selected .react-flow__edge-path{stroke:#555}.react-flow__edge.animated path{stroke-dasharray:5;-webkit-animation:dashdraw .5s linear infinite;animation:dashdraw .5s linear infinite}.react-flow__edge.updating .react-flow__edge-path{stroke:#777}.react-flow__edge-path{stroke:#b1b1b7;stroke-width:1}.react-flow__edge-text{font-size:10px}.react-flow__edge-textbg{fill:#fff}.react-flow__connection-path{stroke:#b1b1b7;stroke-width:1}.react-flow__node{cursor:-webkit-grab;cursor:grab}.react-flow__node-default,.react-flow__node-group,.react-flow__node-input,.react-flow__node-output{background:#fff;border:1px solid #1a192b;border-radius:3px;color:#222;font-size:12px;padding:10px;text-align:center;width:150px}.react-flow__node-default.selected,.react-flow__node-group.selected,.react-flow__node-input.selected,.react-flow__node-output.selected{box-shadow:0 0 0 .5px #1a192b}.react-flow__node-default .react-flow__handle,.react-flow__node-group .react-flow__handle,.react-flow__node-input .react-flow__handle,.react-flow__node-output .react-flow__handle{background:#1a192b}.react-flow__node-default.selectable:hover,.react-flow__node-group.selectable:hover,.react-flow__node-input.selectable:hover,.react-flow__node-output.selectable:hover{box-shadow:0 1px 4px 1px rgba(0,0,0,.08)}.react-flow__node-default.selectable.selected,.react-flow__node-group.selectable.selected,.react-flow__node-input.selectable.selected,.react-flow__node-output.selectable.selected{box-shadow:0 0 0 .5px #1a192b}.react-flow__node-group{background:hsla(0,0%,94%,.25);border-color:#1a192b}.react-flow__nodesselection-rect,.react-flow__selection{background:rgba(0,89,220,.08);border:1px dotted rgba(0,89,220,.8)}.react-flow__handle{background:#555;border:1px solid #fff;border-radius:100%;height:6px;width:6px}.react-flow__handle.connectable{cursor:crosshair}.react-flow__minimap{background-color:#fff}.react-flow__controls{box-shadow:0 0 2px 1px rgba(0,0,0,.08)}.react-flow__controls-button{align-items:center;background:#fefefe;border-bottom:1px solid #eee;box-sizing:content-box;cursor:pointer;display:flex;height:16px;justify-content:center;padding:5px;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;width:16px}.react-flow__controls-button svg{max-height:12px;max-width:12px}.react-flow__controls-button:hover{background:#f4f4f4}";
var shiftX = function shiftX(x, shift, position) {
	if (position === Position.Left) return x - shift;
	if (position === Position.Right) return x + shift;
	return x;
};
var shiftY = function shiftY(y, shift, position) {
	if (position === Position.Top) return y - shift;
	if (position === Position.Bottom) return y + shift;
	return y;
};
var EdgeAnchor = function EdgeAnchor(_ref) {
	var className = _ref.className, position = _ref.position, centerX = _ref.centerX, centerY = _ref.centerY, _ref$radius = _ref.radius, radius = _ref$radius === void 0 ? 10 : _ref$radius;
	return /* @__PURE__ */ import_react.createElement("circle", {
		className: cc(["react-flow__edgeupdater", className]),
		cx: shiftX(centerX, radius, position),
		cy: shiftY(centerY, radius, position),
		r: radius,
		stroke: "transparent",
		fill: "transparent"
	});
};
var wrapEdge = (function(EdgeComponent) {
	var EdgeWrapper = function EdgeWrapper(_ref) {
		var id = _ref.id, className = _ref.className, type = _ref.type, data = _ref.data, onClick = _ref.onClick, onEdgeDoubleClick = _ref.onEdgeDoubleClick, selected = _ref.selected, animated = _ref.animated, label = _ref.label, labelStyle = _ref.labelStyle, labelShowBg = _ref.labelShowBg, labelBgStyle = _ref.labelBgStyle, labelBgPadding = _ref.labelBgPadding, labelBgBorderRadius = _ref.labelBgBorderRadius, style = _ref.style, source = _ref.source, target = _ref.target, sourceX = _ref.sourceX, sourceY = _ref.sourceY, targetX = _ref.targetX, targetY = _ref.targetY, sourcePosition = _ref.sourcePosition, targetPosition = _ref.targetPosition, elementsSelectable = _ref.elementsSelectable, hidden = _ref.hidden, sourceHandleId = _ref.sourceHandleId, targetHandleId = _ref.targetHandleId, onContextMenu = _ref.onContextMenu, onMouseEnter = _ref.onMouseEnter, onMouseMove = _ref.onMouseMove, onMouseLeave = _ref.onMouseLeave, edgeUpdaterRadius = _ref.edgeUpdaterRadius, onEdgeUpdate = _ref.onEdgeUpdate, onEdgeUpdateStart = _ref.onEdgeUpdateStart, onEdgeUpdateEnd = _ref.onEdgeUpdateEnd, markerEnd = _ref.markerEnd, markerStart = _ref.markerStart, rfId = _ref.rfId;
		var _useState2 = _slicedToArray((0, import_react.useState)(false), 2), updating = _useState2[0], setUpdating = _useState2[1];
		var store = useStoreApi();
		var onEdgeClick = function onEdgeClick(event) {
			var _store$getState = store.getState(), edges = _store$getState.edges, addSelectedEdges = _store$getState.addSelectedEdges;
			var edge = edges.find(function(e) {
				return e.id === id;
			});
			if (elementsSelectable) {
				store.setState({ nodesSelectionActive: false });
				addSelectedEdges([id]);
			}
			onClick === null || onClick === void 0 || onClick(event, edge);
		};
		var onEdgeDoubleClickHandler = getMouseHandler(id, store.getState, onEdgeDoubleClick);
		var onEdgeContextMenu = getMouseHandler(id, store.getState, onContextMenu);
		var onEdgeMouseEnter = getMouseHandler(id, store.getState, onMouseEnter);
		var onEdgeMouseMove = getMouseHandler(id, store.getState, onMouseMove);
		var onEdgeMouseLeave = getMouseHandler(id, store.getState, onMouseLeave);
		var handleEdgeUpdater = function handleEdgeUpdater(event, isSourceHandle) {
			var nodeId = isSourceHandle ? target : source;
			var handleId = (isSourceHandle ? targetHandleId : sourceHandleId) || null;
			var handleType = isSourceHandle ? "target" : "source";
			var isValidConnection = function isValidConnection() {
				return true;
			};
			var isTarget = isSourceHandle;
			var edge = store.getState().edges.find(function(e) {
				return e.id === id;
			});
			onEdgeUpdateStart === null || onEdgeUpdateStart === void 0 || onEdgeUpdateStart(event, edge, handleType);
			var _onEdgeUpdateEnd = onEdgeUpdateEnd ? function(evt) {
				return onEdgeUpdateEnd(evt, edge, handleType);
			} : void 0;
			handleMouseDown({
				event,
				handleId,
				nodeId,
				onConnect: function onConnectEdge(connection) {
					return onEdgeUpdate === null || onEdgeUpdate === void 0 ? void 0 : onEdgeUpdate(edge, connection);
				},
				isTarget,
				getState: store.getState,
				setState: store.setState,
				isValidConnection,
				elementEdgeUpdaterType: handleType,
				onEdgeUpdateEnd: _onEdgeUpdateEnd
			});
		};
		var onEdgeUpdaterSourceMouseDown = function onEdgeUpdaterSourceMouseDown(event) {
			return handleEdgeUpdater(event, true);
		};
		var onEdgeUpdaterTargetMouseDown = function onEdgeUpdaterTargetMouseDown(event) {
			return handleEdgeUpdater(event, false);
		};
		var onEdgeUpdaterMouseEnter = function onEdgeUpdaterMouseEnter() {
			return setUpdating(true);
		};
		var onEdgeUpdaterMouseOut = function onEdgeUpdaterMouseOut() {
			return setUpdating(false);
		};
		var markerStartUrl = (0, import_react.useMemo)(function() {
			return "url(#".concat(getMarkerId(markerStart, rfId), ")");
		}, [markerStart, rfId]);
		var markerEndUrl = (0, import_react.useMemo)(function() {
			return "url(#".concat(getMarkerId(markerEnd, rfId), ")");
		}, [markerEnd, rfId]);
		if (hidden) return null;
		var inactive = !elementsSelectable && !onClick;
		var handleEdgeUpdate = typeof onEdgeUpdate !== "undefined";
		var edgeClasses = cc([
			"react-flow__edge",
			"react-flow__edge-".concat(type),
			className,
			{
				selected,
				animated,
				inactive,
				updating
			}
		]);
		return /* @__PURE__ */ import_react.createElement("g", {
			className: edgeClasses,
			onClick: onEdgeClick,
			onDoubleClick: onEdgeDoubleClickHandler,
			onContextMenu: onEdgeContextMenu,
			onMouseEnter: onEdgeMouseEnter,
			onMouseMove: onEdgeMouseMove,
			onMouseLeave: onEdgeMouseLeave
		}, /* @__PURE__ */ import_react.createElement(EdgeComponent, {
			id,
			source,
			target,
			selected,
			animated,
			label,
			labelStyle,
			labelShowBg,
			labelBgStyle,
			labelBgPadding,
			labelBgBorderRadius,
			data,
			style,
			sourceX,
			sourceY,
			targetX,
			targetY,
			sourcePosition,
			targetPosition,
			sourceHandleId,
			targetHandleId,
			markerStart: markerStartUrl,
			markerEnd: markerEndUrl,
			"data-testid": "rf__edge-".concat(id)
		}), handleEdgeUpdate && /* @__PURE__ */ import_react.createElement("g", {
			onMouseDown: onEdgeUpdaterSourceMouseDown,
			onMouseEnter: onEdgeUpdaterMouseEnter,
			onMouseOut: onEdgeUpdaterMouseOut
		}, /* @__PURE__ */ import_react.createElement(EdgeAnchor, {
			position: sourcePosition,
			centerX: sourceX,
			centerY: sourceY,
			radius: edgeUpdaterRadius
		})), handleEdgeUpdate && /* @__PURE__ */ import_react.createElement("g", {
			onMouseDown: onEdgeUpdaterTargetMouseDown,
			onMouseEnter: onEdgeUpdaterMouseEnter,
			onMouseOut: onEdgeUpdaterMouseOut
		}, /* @__PURE__ */ import_react.createElement(EdgeAnchor, {
			position: targetPosition,
			centerX: targetX,
			centerY: targetY,
			radius: edgeUpdaterRadius
		})));
	};
	EdgeWrapper.displayName = "EdgeWrapper";
	return /* @__PURE__ */ (0, import_react.memo)(EdgeWrapper);
});
function ownKeys$8(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$8(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$8(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$8(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function createEdgeTypes(edgeTypes) {
	var standardTypes = {
		"default": wrapEdge(edgeTypes["default"] || BezierEdge),
		straight: wrapEdge(edgeTypes.bezier || StraightEdge),
		step: wrapEdge(edgeTypes.step || StepEdge),
		smoothstep: wrapEdge(edgeTypes.step || SmoothStepEdge),
		simplebezier: wrapEdge(edgeTypes.simplebezier || SimpleBezierEdge)
	};
	var specialTypes = Object.keys(edgeTypes).filter(function(k) {
		return !["default", "bezier"].includes(k);
	}).reduce(function(res, key) {
		res[key] = wrapEdge(edgeTypes[key] || BezierEdge);
		return res;
	}, {});
	return _objectSpread$8(_objectSpread$8({}, standardTypes), specialTypes);
}
function getHandlePosition(position, nodeRect) {
	var handle = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : null;
	var x = ((handle === null || handle === void 0 ? void 0 : handle.x) || 0) + nodeRect.x;
	var y = ((handle === null || handle === void 0 ? void 0 : handle.y) || 0) + nodeRect.y;
	var width = (handle === null || handle === void 0 ? void 0 : handle.width) || nodeRect.width;
	var height = (handle === null || handle === void 0 ? void 0 : handle.height) || nodeRect.height;
	switch (position) {
		case Position.Top: return {
			x: x + width / 2,
			y
		};
		case Position.Right: return {
			x: x + width,
			y: y + height / 2
		};
		case Position.Bottom: return {
			x: x + width / 2,
			y: y + height
		};
		case Position.Left: return {
			x,
			y: y + height / 2
		};
	}
}
function getHandle(bounds, handleId) {
	if (!bounds) return null;
	var handle = null;
	if (bounds.length === 1 || !handleId) handle = bounds[0];
	else if (handleId) handle = bounds.find(function(d) {
		return d.id === handleId;
	});
	return typeof handle === "undefined" ? null : handle;
}
var getEdgePositions = function getEdgePositions(sourceNodeRect, sourceHandle, sourcePosition, targetNodeRect, targetHandle, targetPosition) {
	var sourceHandlePos = getHandlePosition(sourcePosition, sourceNodeRect, sourceHandle);
	var targetHandlePos = getHandlePosition(targetPosition, targetNodeRect, targetHandle);
	return {
		sourceX: sourceHandlePos.x,
		sourceY: sourceHandlePos.y,
		targetX: targetHandlePos.x,
		targetY: targetHandlePos.y
	};
};
function isEdgeVisible(_ref) {
	var sourcePos = _ref.sourcePos, targetPos = _ref.targetPos, sourceWidth = _ref.sourceWidth, sourceHeight = _ref.sourceHeight, targetWidth = _ref.targetWidth, targetHeight = _ref.targetHeight, width = _ref.width, height = _ref.height, transform = _ref.transform;
	var edgeBox = {
		x: Math.min(sourcePos.x, targetPos.x),
		y: Math.min(sourcePos.y, targetPos.y),
		x2: Math.max(sourcePos.x + sourceWidth, targetPos.x + targetWidth),
		y2: Math.max(sourcePos.y + sourceHeight, targetPos.y + targetHeight)
	};
	if (edgeBox.x === edgeBox.x2) edgeBox.x2 += 1;
	if (edgeBox.y === edgeBox.y2) edgeBox.y2 += 1;
	var viewBox = rectToBox({
		x: (0 - transform[0]) / transform[2],
		y: (0 - transform[1]) / transform[2],
		width: width / transform[2],
		height: height / transform[2]
	});
	var xOverlap = Math.max(0, Math.min(viewBox.x2, edgeBox.x2) - Math.max(viewBox.x, edgeBox.x));
	var yOverlap = Math.max(0, Math.min(viewBox.y2, edgeBox.y2) - Math.max(viewBox.y, edgeBox.y));
	return Math.ceil(xOverlap * yOverlap) > 0;
}
function getNodeData(nodeInternals, nodeId) {
	var _node$internalsSymbol, _node$positionAbsolut, _node$positionAbsolut2, _node$positionAbsolut3, _node$positionAbsolut4;
	var node = nodeInternals.get(nodeId);
	var handleBounds = (node === null || node === void 0 ? void 0 : (_node$internalsSymbol = node[internalsSymbol]) === null || _node$internalsSymbol === void 0 ? void 0 : _node$internalsSymbol.handleBounds) || null;
	var isInvalid = !node || !handleBounds || !node.width || !node.height || typeof ((_node$positionAbsolut = node.positionAbsolute) === null || _node$positionAbsolut === void 0 ? void 0 : _node$positionAbsolut.x) === "undefined" || typeof ((_node$positionAbsolut2 = node.positionAbsolute) === null || _node$positionAbsolut2 === void 0 ? void 0 : _node$positionAbsolut2.y) === "undefined";
	return [
		{
			x: (node === null || node === void 0 ? void 0 : (_node$positionAbsolut3 = node.positionAbsolute) === null || _node$positionAbsolut3 === void 0 ? void 0 : _node$positionAbsolut3.x) || 0,
			y: (node === null || node === void 0 ? void 0 : (_node$positionAbsolut4 = node.positionAbsolute) === null || _node$positionAbsolut4 === void 0 ? void 0 : _node$positionAbsolut4.y) || 0,
			width: (node === null || node === void 0 ? void 0 : node.width) || 0,
			height: (node === null || node === void 0 ? void 0 : node.height) || 0
		},
		handleBounds,
		!isInvalid
	];
}
var doc = typeof document !== "undefined" ? document : null;
var useKeyPress = (function() {
	var keyCode = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : null;
	var options = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : { target: doc };
	var _useState2 = _slicedToArray((0, import_react.useState)(false), 2), keyPressed = _useState2[0], setKeyPressed = _useState2[1];
	var pressedKeys = (0, import_react.useRef)(/* @__PURE__ */ new Set([]));
	var _useMemo2 = _slicedToArray((0, import_react.useMemo)(function() {
		if (keyCode !== null) {
			var keys = (Array.isArray(keyCode) ? keyCode : [keyCode]).filter(function(kc) {
				return typeof kc === "string";
			}).map(function(kc) {
				return kc.split("+");
			});
			return [keys, keys.reduce(function(res, item) {
				return res.concat.apply(res, _toConsumableArray(item));
			}, [])];
		}
		return [[], []];
	}, [keyCode]), 2), keyCodes = _useMemo2[0], keysToWatch = _useMemo2[1];
	(0, import_react.useEffect)(function() {
		if (keyCode !== null) {
			var _options$target, _options$target2;
			var downHandler = function downHandler(event) {
				if (isInputDOMNode(event)) return false;
				var keyOrCode = useKeyOrCode(event.code, keysToWatch);
				pressedKeys.current.add(event[keyOrCode]);
				if (isMatchingKey(keyCodes, pressedKeys.current, false)) {
					event.preventDefault();
					setKeyPressed(true);
				}
			};
			var upHandler = function upHandler(event) {
				if (isInputDOMNode(event)) return false;
				var keyOrCode = useKeyOrCode(event.code, keysToWatch);
				if (isMatchingKey(keyCodes, pressedKeys.current, true)) {
					setKeyPressed(false);
					pressedKeys.current.clear();
				} else pressedKeys.current["delete"](event[keyOrCode]);
			};
			var resetHandler = function resetHandler() {
				pressedKeys.current.clear();
				setKeyPressed(false);
			};
			options === null || options === void 0 || (_options$target = options.target) == null || _options$target.addEventListener("keydown", downHandler);
			options === null || options === void 0 || (_options$target2 = options.target) == null || _options$target2.addEventListener("keyup", upHandler);
			window.addEventListener("blur", resetHandler);
			return function() {
				var _options$target3, _options$target4;
				options === null || options === void 0 || (_options$target3 = options.target) == null || _options$target3.removeEventListener("keydown", downHandler);
				options === null || options === void 0 || (_options$target4 = options.target) == null || _options$target4.removeEventListener("keyup", upHandler);
				window.removeEventListener("blur", resetHandler);
			};
		}
	}, [keyCode, setKeyPressed]);
	return keyPressed;
});
function isMatchingKey(keyCodes, pressedKeys, isUp) {
	return keyCodes.filter(function(keys) {
		return isUp || keys.length === pressedKeys.size;
	}).some(function(keys) {
		return keys.every(function(k) {
			return pressedKeys.has(k);
		});
	});
}
function useKeyOrCode(eventCode, keysToWatch) {
	return keysToWatch.includes(eventCode) ? "code" : "key";
}
function isInputDOMNode(event) {
	var _event$composedPath;
	var target = ((_event$composedPath = event.composedPath) === null || _event$composedPath === void 0 ? void 0 : _event$composedPath.call(event)[0]) || event.target;
	return [
		"INPUT",
		"SELECT",
		"TEXTAREA"
	].includes(target === null || target === void 0 ? void 0 : target.nodeName) || (target === null || target === void 0 ? void 0 : target.hasAttribute("contenteditable"));
}
var selector$7 = function selector(s) {
	return {
		onNodesChange: s.onNodesChange,
		onEdgesChange: s.onEdgesChange
	};
};
var useGlobalKeyHandler = (function(_ref) {
	var deleteKeyCode = _ref.deleteKeyCode, multiSelectionKeyCode = _ref.multiSelectionKeyCode;
	var store = useStoreApi();
	var _useStore = useStore(selector$7, shallow), onNodesChange = _useStore.onNodesChange, onEdgesChange = _useStore.onEdgesChange;
	var deleteKeyPressed = useKeyPress(deleteKeyCode);
	var multiSelectionKeyPressed = useKeyPress(multiSelectionKeyCode);
	(0, import_react.useEffect)(function() {
		var _store$getState = store.getState(), nodeInternals = _store$getState.nodeInternals, edges = _store$getState.edges, hasDefaultNodes = _store$getState.hasDefaultNodes, hasDefaultEdges = _store$getState.hasDefaultEdges, onNodesDelete = _store$getState.onNodesDelete, onEdgesDelete = _store$getState.onEdgesDelete;
		var nodesToRemove = Array.from(nodeInternals.values()).reduce(function(res, node) {
			if (!node.selected && node.parentNode && res.find(function(n) {
				return n.id === node.parentNode;
			})) res.push(node);
			else if (node.selected) res.push(node);
			return res;
		}, []);
		var selectedEdges = edges.filter(function(e) {
			return e.selected;
		});
		if (deleteKeyPressed && (nodesToRemove || selectedEdges)) {
			var connectedEdges = getConnectedEdges(nodesToRemove, edges);
			var edgesToRemove = [].concat(_toConsumableArray(selectedEdges), _toConsumableArray(connectedEdges));
			var edgeIdsToRemove = edgesToRemove.reduce(function(res, edge) {
				if (!res.includes(edge.id)) res.push(edge.id);
				return res;
			}, []);
			if (hasDefaultEdges || hasDefaultNodes) {
				if (hasDefaultEdges) store.setState({ edges: edges.filter(function(e) {
					return !edgeIdsToRemove.includes(e.id);
				}) });
				if (hasDefaultNodes) {
					nodesToRemove.forEach(function(node) {
						nodeInternals["delete"](node.id);
					});
					store.setState({ nodeInternals: new Map(nodeInternals) });
				}
			}
			if (edgeIdsToRemove.length > 0) {
				onEdgesDelete === null || onEdgesDelete === void 0 || onEdgesDelete(edgesToRemove);
				if (onEdgesChange) onEdgesChange(edgeIdsToRemove.map(function(id) {
					return {
						id,
						type: "remove"
					};
				}));
			}
			if (nodesToRemove.length > 0) {
				onNodesDelete === null || onNodesDelete === void 0 || onNodesDelete(nodesToRemove);
				if (onNodesChange) onNodesChange(nodesToRemove.map(function(n) {
					return {
						id: n.id,
						type: "remove"
					};
				}));
			}
			store.setState({ nodesSelectionActive: false });
		}
	}, [
		deleteKeyPressed,
		onNodesChange,
		onEdgesChange
	]);
	(0, import_react.useEffect)(function() {
		store.setState({ multiSelectionActive: multiSelectionKeyPressed });
	}, [multiSelectionKeyPressed]);
});
function useResizeHandler(rendererNode) {
	var store = useStoreApi();
	(0, import_react.useEffect)(function() {
		var resizeObserver;
		var updateDimensions = function updateDimensions() {
			if (!rendererNode.current) return;
			var size = getDimensions(rendererNode.current);
			if (size.height === 0 || size.width === 0) console.warn("[React Flow]: The React Flow parent container needs a width and a height to render the graph. Help: https://reactflow.dev/error#400");
			store.setState({
				width: size.width || 500,
				height: size.height || 500
			});
		};
		updateDimensions();
		window.onresize = updateDimensions;
		if (rendererNode.current) {
			resizeObserver = new ResizeObserver(function() {
				return updateDimensions();
			});
			resizeObserver.observe(rendererNode.current);
		}
		return function() {
			window.onresize = null;
			if (resizeObserver && rendererNode.current) resizeObserver.unobserve(rendererNode.current);
		};
	}, []);
}
var viewChanged = function viewChanged(prevViewport, eventViewport) {
	return prevViewport.x !== eventViewport.x || prevViewport.y !== eventViewport.y || prevViewport.zoom !== eventViewport.k;
};
var eventToFlowTransform = function eventToFlowTransform(eventViewport) {
	return {
		x: eventViewport.x,
		y: eventViewport.y,
		zoom: eventViewport.k
	};
};
var isWrappedWithClass = function isWrappedWithClass(event, className) {
	return event.target.closest(".".concat(className));
};
var selector$6 = function selector(s) {
	return {
		d3Zoom: s.d3Zoom,
		d3Selection: s.d3Selection,
		d3ZoomHandler: s.d3ZoomHandler
	};
};
var ZoomPane = function ZoomPane(_ref) {
	var onMove = _ref.onMove, onMoveStart = _ref.onMoveStart, onMoveEnd = _ref.onMoveEnd, _ref$zoomOnScroll = _ref.zoomOnScroll, zoomOnScroll = _ref$zoomOnScroll === void 0 ? true : _ref$zoomOnScroll, _ref$zoomOnPinch = _ref.zoomOnPinch, zoomOnPinch = _ref$zoomOnPinch === void 0 ? true : _ref$zoomOnPinch, _ref$panOnScroll = _ref.panOnScroll, panOnScroll = _ref$panOnScroll === void 0 ? false : _ref$panOnScroll, _ref$panOnScrollSpeed = _ref.panOnScrollSpeed, panOnScrollSpeed = _ref$panOnScrollSpeed === void 0 ? .5 : _ref$panOnScrollSpeed, _ref$panOnScrollMode = _ref.panOnScrollMode, panOnScrollMode = _ref$panOnScrollMode === void 0 ? PanOnScrollMode.Free : _ref$panOnScrollMode, _ref$zoomOnDoubleClic = _ref.zoomOnDoubleClick, zoomOnDoubleClick = _ref$zoomOnDoubleClic === void 0 ? true : _ref$zoomOnDoubleClic, selectionKeyPressed = _ref.selectionKeyPressed, elementsSelectable = _ref.elementsSelectable, _ref$panOnDrag = _ref.panOnDrag, panOnDrag = _ref$panOnDrag === void 0 ? true : _ref$panOnDrag, translateExtent = _ref.translateExtent, minZoom = _ref.minZoom, maxZoom = _ref.maxZoom, _ref$defaultZoom = _ref.defaultZoom, defaultZoom = _ref$defaultZoom === void 0 ? 1 : _ref$defaultZoom, _ref$defaultPosition = _ref.defaultPosition, defaultPosition = _ref$defaultPosition === void 0 ? [0, 0] : _ref$defaultPosition, zoomActivationKeyCode = _ref.zoomActivationKeyCode, _ref$preventScrolling = _ref.preventScrolling, preventScrolling = _ref$preventScrolling === void 0 ? true : _ref$preventScrolling, children = _ref.children, noWheelClassName = _ref.noWheelClassName, noPanClassName = _ref.noPanClassName;
	var store = useStoreApi();
	var isZoomingOrPanning = (0, import_react.useRef)(false);
	var zoomPane = (0, import_react.useRef)(null);
	var prevTransform = (0, import_react.useRef)({
		x: 0,
		y: 0,
		zoom: 0
	});
	var _useStore = useStore(selector$6, shallow), d3Zoom = _useStore.d3Zoom, d3Selection = _useStore.d3Selection, d3ZoomHandler = _useStore.d3ZoomHandler;
	var zoomActivationKeyPressed = useKeyPress(zoomActivationKeyCode);
	useResizeHandler(zoomPane);
	(0, import_react.useEffect)(function() {
		if (zoomPane.current) {
			var _selection$node;
			var d3ZoomInstance = zoom_default().scaleExtent([minZoom, maxZoom]).translateExtent(translateExtent);
			var selection = select_default$1(zoomPane.current).call(d3ZoomInstance);
			var clampedX = clamp(defaultPosition[0], translateExtent[0][0], translateExtent[1][0]);
			var clampedY = clamp(defaultPosition[1], translateExtent[0][1], translateExtent[1][1]);
			var clampedZoom = clamp(defaultZoom, minZoom, maxZoom);
			var updatedTransform = identity.translate(clampedX, clampedY).scale(clampedZoom);
			d3ZoomInstance.transform(selection, updatedTransform);
			store.setState({
				d3Zoom: d3ZoomInstance,
				d3Selection: selection,
				d3ZoomHandler: selection.on("wheel.zoom"),
				transform: [
					clampedX,
					clampedY,
					clampedZoom
				],
				domNode: (_selection$node = selection.node()) === null || _selection$node === void 0 ? void 0 : _selection$node.closest(".react-flow")
			});
		}
	}, []);
	(0, import_react.useEffect)(function() {
		if (d3Selection && d3Zoom) {
			if (panOnScroll && !zoomActivationKeyPressed) d3Selection.on("wheel", function(event) {
				if (isWrappedWithClass(event, noWheelClassName)) return false;
				event.preventDefault();
				event.stopImmediatePropagation();
				var currentZoom = d3Selection.property("__zoom").k || 1;
				if (event.ctrlKey && zoomOnPinch) {
					var point = pointer_default(event);
					var pinchDelta = -event.deltaY * (event.deltaMode === 1 ? .05 : event.deltaMode ? 1 : .002) * 10;
					var _zoom = currentZoom * Math.pow(2, pinchDelta);
					d3Zoom.scaleTo(d3Selection, _zoom, point);
					return;
				}
				var deltaNormalize = event.deltaMode === 1 ? 20 : 1;
				var deltaX = panOnScrollMode === PanOnScrollMode.Vertical ? 0 : event.deltaX * deltaNormalize;
				var deltaY = panOnScrollMode === PanOnScrollMode.Horizontal ? 0 : event.deltaY * deltaNormalize;
				d3Zoom.translateBy(d3Selection, -(deltaX / currentZoom) * panOnScrollSpeed, -(deltaY / currentZoom) * panOnScrollSpeed);
			}).on("wheel.zoom", null);
			else if (typeof d3ZoomHandler !== "undefined") d3Selection.on("wheel", function(event) {
				if (!preventScrolling || isWrappedWithClass(event, noWheelClassName)) return null;
				event.preventDefault();
			}).on("wheel.zoom", d3ZoomHandler);
		}
	}, [
		panOnScroll,
		panOnScrollMode,
		d3Selection,
		d3Zoom,
		d3ZoomHandler,
		zoomActivationKeyPressed,
		zoomOnPinch,
		preventScrolling,
		noWheelClassName
	]);
	(0, import_react.useEffect)(function() {
		if (d3Zoom) {
			if (selectionKeyPressed && !isZoomingOrPanning.current) d3Zoom.on("zoom", null);
			else if (!selectionKeyPressed) d3Zoom.on("zoom", function(event) {
				store.setState({ transform: [
					event.transform.x,
					event.transform.y,
					event.transform.k
				] });
				if (onMove) {
					var flowTransform = eventToFlowTransform(event.transform);
					onMove(event.sourceEvent, flowTransform);
				}
			});
		}
	}, [
		selectionKeyPressed,
		d3Zoom,
		onMove
	]);
	(0, import_react.useEffect)(function() {
		if (d3Zoom) d3Zoom.on("start", function(event) {
			isZoomingOrPanning.current = true;
			if (onMoveStart) {
				var flowTransform = eventToFlowTransform(event.transform);
				prevTransform.current = flowTransform;
				onMoveStart(event.sourceEvent, flowTransform);
			}
		});
	}, [d3Zoom, onMoveStart]);
	(0, import_react.useEffect)(function() {
		if (d3Zoom) d3Zoom.on("end", function(event) {
			isZoomingOrPanning.current = false;
			if (onMoveEnd && viewChanged(prevTransform.current, event.transform)) {
				var flowTransform = eventToFlowTransform(event.transform);
				prevTransform.current = flowTransform;
				onMoveEnd(event.sourceEvent, flowTransform);
			}
		});
	}, [d3Zoom, onMoveEnd]);
	(0, import_react.useEffect)(function() {
		if (d3Zoom) d3Zoom.filter(function(event) {
			var zoomScroll = zoomActivationKeyPressed || zoomOnScroll;
			var pinchZoom = zoomOnPinch && event.ctrlKey;
			if (!panOnDrag && !zoomScroll && !panOnScroll && !zoomOnDoubleClick && !zoomOnPinch) return false;
			if (selectionKeyPressed) return false;
			if (!zoomOnDoubleClick && event.type === "dblclick") return false;
			if (isWrappedWithClass(event, noWheelClassName) && event.type === "wheel") return false;
			if (isWrappedWithClass(event, noPanClassName) && event.type !== "wheel") return false;
			if (!zoomOnPinch && event.ctrlKey && event.type === "wheel") return false;
			if (!zoomScroll && !panOnScroll && !pinchZoom && event.type === "wheel") return false;
			if (!panOnDrag && (event.type === "mousedown" || event.type === "touchstart")) return false;
			return (!event.ctrlKey || event.type === "wheel") && !event.button;
		});
	}, [
		d3Zoom,
		zoomOnScroll,
		zoomOnPinch,
		panOnScroll,
		zoomOnDoubleClick,
		panOnDrag,
		selectionKeyPressed,
		elementsSelectable,
		zoomActivationKeyPressed
	]);
	return /* @__PURE__ */ import_react.createElement("div", {
		className: "react-flow__renderer react-flow__container",
		ref: zoomPane
	}, children);
};
function ownKeys$7(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$7(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$7(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$7(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function getMousePosition(event, containerBounds) {
	return {
		x: event.clientX - containerBounds.left,
		y: event.clientY - containerBounds.top
	};
}
var selector$5 = function selector(s) {
	return {
		userSelectionActive: s.userSelectionActive,
		elementsSelectable: s.elementsSelectable
	};
};
var initialRect = {
	startX: 0,
	startY: 0,
	x: 0,
	y: 0,
	width: 0,
	height: 0,
	draw: false
};
var UserSelection = /* @__PURE__ */ (0, import_react.memo)(function(_ref) {
	var selectionKeyPressed = _ref.selectionKeyPressed;
	var store = useStoreApi();
	var prevSelectedNodesCount = (0, import_react.useRef)(0);
	var prevSelectedEdgesCount = (0, import_react.useRef)(0);
	var containerBounds = (0, import_react.useRef)();
	var _useState2 = _slicedToArray((0, import_react.useState)(initialRect), 2), userSelectionRect = _useState2[0], setUserSelectionRect = _useState2[1];
	var _useStore = useStore(selector$5, shallow), userSelectionActive = _useStore.userSelectionActive;
	if (!_useStore.elementsSelectable || !(userSelectionActive || selectionKeyPressed)) return null;
	var resetUserSelection = function resetUserSelection() {
		setUserSelectionRect(initialRect);
		store.setState({ userSelectionActive: false });
		prevSelectedNodesCount.current = 0;
		prevSelectedEdgesCount.current = 0;
	};
	return /* @__PURE__ */ import_react.createElement("div", {
		className: "react-flow__selectionpane react-flow__container",
		onMouseDown: function onMouseDown(event) {
			containerBounds.current = event.target.closest(".react-flow").getBoundingClientRect();
			var mousePos = getMousePosition(event, containerBounds.current);
			setUserSelectionRect({
				width: 0,
				height: 0,
				startX: mousePos.x,
				startY: mousePos.y,
				x: mousePos.x,
				y: mousePos.y,
				draw: true
			});
			store.setState({
				userSelectionActive: true,
				nodesSelectionActive: false
			});
		},
		onMouseMove: function onMouseMove(event) {
			var _userSelectionRect$st, _userSelectionRect$st2;
			if (!selectionKeyPressed || !userSelectionRect.draw || !containerBounds.current) return;
			var mousePos = getMousePosition(event, containerBounds.current);
			var startX = (_userSelectionRect$st = userSelectionRect.startX) !== null && _userSelectionRect$st !== void 0 ? _userSelectionRect$st : 0;
			var startY = (_userSelectionRect$st2 = userSelectionRect.startY) !== null && _userSelectionRect$st2 !== void 0 ? _userSelectionRect$st2 : 0;
			var nextUserSelectRect = _objectSpread$7(_objectSpread$7({}, userSelectionRect), {}, {
				x: mousePos.x < startX ? mousePos.x : startX,
				y: mousePos.y < startY ? mousePos.y : startY,
				width: Math.abs(mousePos.x - startX),
				height: Math.abs(mousePos.y - startY)
			});
			var _store$getState = store.getState(), nodeInternals = _store$getState.nodeInternals, edges = _store$getState.edges, transform = _store$getState.transform, onNodesChange = _store$getState.onNodesChange, onEdgesChange = _store$getState.onEdgesChange;
			var nodes = Array.from(nodeInternals.values());
			var selectedNodes = getNodesInside(nodeInternals, nextUserSelectRect, transform, false, true);
			var selectedEdgeIds = getConnectedEdges(selectedNodes, edges).map(function(e) {
				return e.id;
			});
			var selectedNodeIds = selectedNodes.map(function(n) {
				return n.id;
			});
			if (prevSelectedNodesCount.current !== selectedNodeIds.length) {
				prevSelectedNodesCount.current = selectedNodeIds.length;
				var changes = getSelectionChanges(nodes, selectedNodeIds);
				if (changes.length) onNodesChange === null || onNodesChange === void 0 || onNodesChange(changes);
			}
			if (prevSelectedEdgesCount.current !== selectedEdgeIds.length) {
				prevSelectedEdgesCount.current = selectedEdgeIds.length;
				var _changes = getSelectionChanges(edges, selectedEdgeIds);
				if (_changes.length) onEdgesChange === null || onEdgesChange === void 0 || onEdgesChange(_changes);
			}
			setUserSelectionRect(nextUserSelectRect);
		},
		onMouseUp: function onMouseUp() {
			store.setState({ nodesSelectionActive: prevSelectedNodesCount.current > 0 });
			resetUserSelection();
		},
		onMouseLeave: function onMouseLeave() {
			store.setState({ nodesSelectionActive: false });
			resetUserSelection();
		}
	}, userSelectionRect.draw && /* @__PURE__ */ import_react.createElement("div", {
		className: "react-flow__selection react-flow__container",
		style: {
			width: userSelectionRect.width,
			height: userSelectionRect.height,
			transform: "translate(".concat(userSelectionRect.x, "px, ").concat(userSelectionRect.y, "px)")
		}
	}));
});
function ownKeys$6(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$6(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$6(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$6(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function isParentSelected(node, nodeInternals) {
	if (!node.parentNode) return false;
	var parentNode = nodeInternals.get(node.parentNode);
	if (!parentNode) return false;
	if (parentNode.selected) return true;
	return isParentSelected(parentNode, nodeInternals);
}
function hasSelector(target, selector, nodeRef) {
	var current = target;
	do {
		var _current;
		if ((_current = current) !== null && _current !== void 0 && _current.matches(selector)) return true;
		if (current === nodeRef.current) return false;
		current = current.parentElement;
	} while (current);
	return false;
}
function getDragItems(nodeInternals, mousePos, nodeId) {
	return Array.from(nodeInternals.values()).filter(function(n) {
		return (n.selected || n.id === nodeId) && (!n.parentNode || !isParentSelected(n, nodeInternals));
	}).map(function(n) {
		var _n$positionAbsolute$x, _n$positionAbsolute, _n$positionAbsolute$y, _n$positionAbsolute2;
		return {
			id: n.id,
			position: n.position || {
				x: 0,
				y: 0
			},
			positionAbsolute: n.positionAbsolute || {
				x: 0,
				y: 0
			},
			distance: {
				x: mousePos.x - ((_n$positionAbsolute$x = (_n$positionAbsolute = n.positionAbsolute) === null || _n$positionAbsolute === void 0 ? void 0 : _n$positionAbsolute.x) !== null && _n$positionAbsolute$x !== void 0 ? _n$positionAbsolute$x : 0),
				y: mousePos.y - ((_n$positionAbsolute$y = (_n$positionAbsolute2 = n.positionAbsolute) === null || _n$positionAbsolute2 === void 0 ? void 0 : _n$positionAbsolute2.y) !== null && _n$positionAbsolute$y !== void 0 ? _n$positionAbsolute$y : 0)
			},
			delta: {
				x: 0,
				y: 0
			},
			extent: n.extent,
			parentNode: n.parentNode,
			width: n.width,
			height: n.height
		};
	});
}
function updatePosition(dragItem, mousePos, snapToGrid, _ref, nodeInternals, nodeExtent) {
	var _ref2 = _slicedToArray(_ref, 2), snapX = _ref2[0], snapY = _ref2[1];
	var currentExtent = dragItem.extent || nodeExtent;
	var nextPosition = {
		x: mousePos.x - dragItem.distance.x,
		y: mousePos.y - dragItem.distance.y
	};
	if (snapToGrid) {
		nextPosition.x = snapX * Math.round(nextPosition.x / snapX);
		nextPosition.y = snapY * Math.round(nextPosition.y / snapY);
	}
	if (dragItem.extent === "parent") if (dragItem.parentNode && dragItem.width && dragItem.height) {
		var parent = nodeInternals.get(dragItem.parentNode);
		currentExtent = parent !== null && parent !== void 0 && parent.positionAbsolute && parent !== null && parent !== void 0 && parent.width && parent !== null && parent !== void 0 && parent.height ? [[parent.positionAbsolute.x, parent.positionAbsolute.y], [parent.positionAbsolute.x + parent.width - dragItem.width, parent.positionAbsolute.y + parent.height - dragItem.height]] : currentExtent;
	} else {
		console.warn("[React Flow]: Only child nodes can use a parent extent. Help: https://reactflow.dev/error#500");
		currentExtent = nodeExtent;
	}
	else if (dragItem.extent && dragItem.parentNode) {
		var _parent$positionAbsol, _parent$positionAbsol2, _parent$positionAbsol3, _parent$positionAbsol4;
		var _parent = nodeInternals.get(dragItem.parentNode);
		var parentX = (_parent$positionAbsol = _parent === null || _parent === void 0 ? void 0 : (_parent$positionAbsol2 = _parent.positionAbsolute) === null || _parent$positionAbsol2 === void 0 ? void 0 : _parent$positionAbsol2.x) !== null && _parent$positionAbsol !== void 0 ? _parent$positionAbsol : 0;
		var parentY = (_parent$positionAbsol3 = _parent === null || _parent === void 0 ? void 0 : (_parent$positionAbsol4 = _parent.positionAbsolute) === null || _parent$positionAbsol4 === void 0 ? void 0 : _parent$positionAbsol4.y) !== null && _parent$positionAbsol3 !== void 0 ? _parent$positionAbsol3 : 0;
		currentExtent = [[dragItem.extent[0][0] + parentX, dragItem.extent[0][1] + parentY], [dragItem.extent[1][0] + parentX, dragItem.extent[1][1] + parentY]];
	}
	var parentPosition = {
		x: 0,
		y: 0
	};
	if (dragItem.parentNode) {
		var _parentNode$positionA, _parentNode$positionA2, _parentNode$positionA3, _parentNode$positionA4;
		var parentNode = nodeInternals.get(dragItem.parentNode);
		parentPosition = {
			x: (_parentNode$positionA = parentNode === null || parentNode === void 0 ? void 0 : (_parentNode$positionA2 = parentNode.positionAbsolute) === null || _parentNode$positionA2 === void 0 ? void 0 : _parentNode$positionA2.x) !== null && _parentNode$positionA !== void 0 ? _parentNode$positionA : 0,
			y: (_parentNode$positionA3 = parentNode === null || parentNode === void 0 ? void 0 : (_parentNode$positionA4 = parentNode.positionAbsolute) === null || _parentNode$positionA4 === void 0 ? void 0 : _parentNode$positionA4.y) !== null && _parentNode$positionA3 !== void 0 ? _parentNode$positionA3 : 0
		};
	}
	dragItem.positionAbsolute = currentExtent ? clampPosition(nextPosition, currentExtent) : nextPosition;
	dragItem.position = {
		x: dragItem.positionAbsolute.x - parentPosition.x,
		y: dragItem.positionAbsolute.y - parentPosition.y
	};
	return dragItem;
}
function getEventHandlerParams(_ref3) {
	var nodeId = _ref3.nodeId, dragItems = _ref3.dragItems, nodeInternals = _ref3.nodeInternals;
	var extentedDragItems = dragItems.map(function(n) {
		return _objectSpread$6(_objectSpread$6({}, nodeInternals.get(n.id)), {}, {
			position: n.position,
			positionAbsolute: n.positionAbsolute
		});
	});
	return [nodeId ? extentedDragItems.find(function(n) {
		return n.id === nodeId;
	}) : extentedDragItems[0], extentedDragItems];
}
function wrapSelectionDragFunc(selectionFunc) {
	return function(event, _, nodes) {
		return selectionFunc === null || selectionFunc === void 0 ? void 0 : selectionFunc(event, nodes);
	};
}
function useDrag(_ref) {
	var nodeRef = _ref.nodeRef, _ref$disabled = _ref.disabled, disabled = _ref$disabled === void 0 ? false : _ref$disabled, noDragClassName = _ref.noDragClassName, handleSelector = _ref.handleSelector, nodeId = _ref.nodeId, isSelectable = _ref.isSelectable, selectNodesOnDrag = _ref.selectNodesOnDrag;
	var _useState2 = _slicedToArray((0, import_react.useState)(false), 2), dragging = _useState2[0], setDragging = _useState2[1];
	var store = useStoreApi();
	var dragItems = (0, import_react.useRef)();
	var lastPos = (0, import_react.useRef)({
		x: null,
		y: null
	});
	var getPointerPosition = (0, import_react.useCallback)(function(_ref2) {
		var sourceEvent = _ref2.sourceEvent;
		var _store$getState = store.getState(), transform = _store$getState.transform, snapGrid = _store$getState.snapGrid, snapToGrid = _store$getState.snapToGrid;
		return pointToRendererPoint({
			x: sourceEvent.touches ? sourceEvent.touches[0].clientX : sourceEvent.clientX,
			y: sourceEvent.touches ? sourceEvent.touches[0].clientY : sourceEvent.clientY
		}, transform, snapToGrid, snapGrid);
	}, []);
	(0, import_react.useEffect)(function() {
		if (nodeRef !== null && nodeRef !== void 0 && nodeRef.current) {
			var selection = select_default$1(nodeRef.current);
			if (disabled) selection.on(".drag", null);
			else {
				var dragHandler = drag_default().on("start", function(event) {
					var _store$getState2 = store.getState(), nodeInternals = _store$getState2.nodeInternals, multiSelectionActive = _store$getState2.multiSelectionActive, unselectNodesAndEdges = _store$getState2.unselectNodesAndEdges, onNodeDragStart = _store$getState2.onNodeDragStart, onSelectionDragStart = _store$getState2.onSelectionDragStart;
					var onStart = nodeId ? onNodeDragStart : wrapSelectionDragFunc(onSelectionDragStart);
					if (!selectNodesOnDrag && !multiSelectionActive && nodeId) {
						var _nodeInternals$get;
						if (!((_nodeInternals$get = nodeInternals.get(nodeId)) !== null && _nodeInternals$get !== void 0 && _nodeInternals$get.selected)) unselectNodesAndEdges();
					}
					if (nodeId && isSelectable && selectNodesOnDrag) handleNodeClick({
						id: nodeId,
						store
					});
					var pointerPos = getPointerPosition(event);
					lastPos.current = pointerPos;
					dragItems.current = getDragItems(nodeInternals, pointerPos, nodeId);
					if (onStart && dragItems.current) {
						var _getEventHandlerParam2 = _slicedToArray(getEventHandlerParams({
							nodeId,
							dragItems: dragItems.current,
							nodeInternals
						}), 2), currentNode = _getEventHandlerParam2[0], nodes = _getEventHandlerParam2[1];
						onStart(event.sourceEvent, currentNode, nodes);
					}
				}).on("drag", function(event) {
					var _store$getState3 = store.getState(), updateNodePositions = _store$getState3.updateNodePositions, snapToGrid = _store$getState3.snapToGrid, snapGrid = _store$getState3.snapGrid, nodeInternals = _store$getState3.nodeInternals, nodeExtent = _store$getState3.nodeExtent, onNodeDrag = _store$getState3.onNodeDrag, onSelectionDrag = _store$getState3.onSelectionDrag;
					var pointerPos = getPointerPosition(event);
					if ((lastPos.current.x !== pointerPos.x || lastPos.current.y !== pointerPos.y) && dragItems.current) {
						lastPos.current = pointerPos;
						dragItems.current = dragItems.current.map(function(n) {
							return updatePosition(n, pointerPos, snapToGrid, snapGrid, nodeInternals, nodeExtent);
						});
						var onDrag = nodeId ? onNodeDrag : wrapSelectionDragFunc(onSelectionDrag);
						updateNodePositions(dragItems.current, true, true);
						setDragging(true);
						if (onDrag) {
							var _getEventHandlerParam4 = _slicedToArray(getEventHandlerParams({
								nodeId,
								dragItems: dragItems.current,
								nodeInternals
							}), 2), currentNode = _getEventHandlerParam4[0], nodes = _getEventHandlerParam4[1];
							onDrag(event.sourceEvent, currentNode, nodes);
						}
					}
					event.on("end", function(event) {
						setDragging(false);
						if (dragItems.current) {
							var _store$getState4 = store.getState(), _updateNodePositions = _store$getState4.updateNodePositions, _nodeInternals = _store$getState4.nodeInternals, onNodeDragStop = _store$getState4.onNodeDragStop, onSelectionDragStop = _store$getState4.onSelectionDragStop;
							var onStop = nodeId ? onNodeDragStop : wrapSelectionDragFunc(onSelectionDragStop);
							_updateNodePositions(dragItems.current, false, false);
							if (onStop) {
								var _getEventHandlerParam6 = _slicedToArray(getEventHandlerParams({
									nodeId,
									dragItems: dragItems.current,
									nodeInternals: _nodeInternals
								}), 2), _currentNode = _getEventHandlerParam6[0], _nodes = _getEventHandlerParam6[1];
								onStop(event.sourceEvent, _currentNode, _nodes);
							}
						}
					});
				}).filter(function(event) {
					var target = event.target;
					return !event.button && (!noDragClassName || !hasSelector(target, ".".concat(noDragClassName), nodeRef)) && (!handleSelector || hasSelector(target, handleSelector, nodeRef));
				});
				selection.call(dragHandler);
				return function() {
					selection.on(".drag", null);
				};
			}
		}
	}, [
		nodeRef,
		disabled,
		noDragClassName,
		handleSelector,
		isSelectable,
		store,
		nodeId,
		selectNodesOnDrag,
		getPointerPosition
	]);
	return dragging;
}
function ownKeys$5(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$5(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$5(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$5(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var selector$4 = function selector(s) {
	return _objectSpread$5({
		transformString: "translate(".concat(s.transform[0], "px,").concat(s.transform[1], "px) scale(").concat(s.transform[2], ")"),
		userSelectionActive: s.userSelectionActive
	}, getRectOfNodes(Array.from(s.nodeInternals.values()).filter(function(n) {
		return n.selected;
	})));
};
var bboxSelector = function bboxSelector(s) {
	return getRectOfNodes(Array.from(s.nodeInternals.values()).filter(function(n) {
		return n.selected;
	}));
};
function NodesSelection(_ref) {
	var onSelectionContextMenu = _ref.onSelectionContextMenu, noPanClassName = _ref.noPanClassName;
	var store = useStoreApi();
	var _useStore = useStore(selector$4, shallow), transformString = _useStore.transformString, userSelectionActive = _useStore.userSelectionActive;
	var _useStore2 = useStore(bboxSelector, shallow), width = _useStore2.width, height = _useStore2.height, left = _useStore2.x, top = _useStore2.y;
	var nodeRef = (0, import_react.useRef)(null);
	useDrag({ nodeRef });
	if (userSelectionActive || !width || !height) return null;
	var onContextMenu = onSelectionContextMenu ? function(event) {
		onSelectionContextMenu(event, Array.from(store.getState().nodeInternals.values()).filter(function(n) {
			return n.selected;
		}));
	} : void 0;
	return /* @__PURE__ */ import_react.createElement("div", {
		className: cc([
			"react-flow__nodesselection",
			"react-flow__container",
			noPanClassName
		]),
		style: { transform: transformString }
	}, /* @__PURE__ */ import_react.createElement("div", {
		ref: nodeRef,
		className: "react-flow__nodesselection-rect",
		onContextMenu,
		style: {
			width,
			height,
			top,
			left
		}
	}));
}
var NodesSelection$1 = /* @__PURE__ */ (0, import_react.memo)(NodesSelection);
var selector$3 = function selector(s) {
	return s.nodesSelectionActive;
};
var FlowRenderer = function FlowRenderer(_ref) {
	var children = _ref.children, onPaneClick = _ref.onPaneClick, onPaneContextMenu = _ref.onPaneContextMenu, onPaneScroll = _ref.onPaneScroll, deleteKeyCode = _ref.deleteKeyCode, onMove = _ref.onMove, onMoveStart = _ref.onMoveStart, onMoveEnd = _ref.onMoveEnd, selectionKeyCode = _ref.selectionKeyCode, multiSelectionKeyCode = _ref.multiSelectionKeyCode, zoomActivationKeyCode = _ref.zoomActivationKeyCode, elementsSelectable = _ref.elementsSelectable, zoomOnScroll = _ref.zoomOnScroll, zoomOnPinch = _ref.zoomOnPinch, panOnScroll = _ref.panOnScroll, panOnScrollSpeed = _ref.panOnScrollSpeed, panOnScrollMode = _ref.panOnScrollMode, zoomOnDoubleClick = _ref.zoomOnDoubleClick, panOnDrag = _ref.panOnDrag, translateExtent = _ref.translateExtent, minZoom = _ref.minZoom, maxZoom = _ref.maxZoom, defaultZoom = _ref.defaultZoom, defaultPosition = _ref.defaultPosition, preventScrolling = _ref.preventScrolling, onSelectionContextMenu = _ref.onSelectionContextMenu, noWheelClassName = _ref.noWheelClassName, noPanClassName = _ref.noPanClassName;
	var store = useStoreApi();
	var nodesSelectionActive = useStore(selector$3);
	var selectionKeyPressed = useKeyPress(selectionKeyCode);
	useGlobalKeyHandler({
		deleteKeyCode,
		multiSelectionKeyCode
	});
	var onClick = function onClick(event) {
		onPaneClick === null || onPaneClick === void 0 || onPaneClick(event);
		store.getState().resetSelectedElements();
		store.setState({ nodesSelectionActive: false });
	};
	var onContextMenu = onPaneContextMenu ? function(event) {
		return onPaneContextMenu(event);
	} : void 0;
	var onWheel = onPaneScroll ? function(event) {
		return onPaneScroll(event);
	} : void 0;
	return /* @__PURE__ */ import_react.createElement(ZoomPane, {
		onMove,
		onMoveStart,
		onMoveEnd,
		selectionKeyPressed,
		elementsSelectable,
		zoomOnScroll,
		zoomOnPinch,
		panOnScroll,
		panOnScrollSpeed,
		panOnScrollMode,
		zoomOnDoubleClick,
		panOnDrag,
		translateExtent,
		minZoom,
		maxZoom,
		defaultZoom,
		defaultPosition,
		zoomActivationKeyCode,
		preventScrolling,
		noWheelClassName,
		noPanClassName
	}, children, /* @__PURE__ */ import_react.createElement(UserSelection, { selectionKeyPressed }), nodesSelectionActive && /* @__PURE__ */ import_react.createElement(NodesSelection$1, {
		onSelectionContextMenu,
		noPanClassName
	}), /* @__PURE__ */ import_react.createElement("div", {
		className: "react-flow__pane react-flow__container",
		onClick,
		onContextMenu,
		onWheel
	}));
};
FlowRenderer.displayName = "FlowRenderer";
var FlowRenderer$1 = /* @__PURE__ */ (0, import_react.memo)(FlowRenderer);
function useVisibleNodes(onlyRenderVisible) {
	return useStore((0, import_react.useCallback)(function(s) {
		return onlyRenderVisible ? getNodesInside(s.nodeInternals, {
			x: 0,
			y: 0,
			width: s.width,
			height: s.height
		}, s.transform, true) : Array.from(s.nodeInternals.values());
	}, [onlyRenderVisible]));
}
var selector$2 = function selector(s) {
	return {
		nodesDraggable: s.nodesDraggable,
		nodesConnectable: s.nodesConnectable,
		elementsSelectable: s.elementsSelectable,
		updateNodeDimensions: s.updateNodeDimensions
	};
};
var NodeRenderer = function NodeRenderer(props) {
	var _useStore = useStore(selector$2, shallow), nodesDraggable = _useStore.nodesDraggable, nodesConnectable = _useStore.nodesConnectable, elementsSelectable = _useStore.elementsSelectable, updateNodeDimensions = _useStore.updateNodeDimensions;
	var nodes = useVisibleNodes(props.onlyRenderVisibleElements);
	var resizeObserverRef = (0, import_react.useRef)();
	var resizeObserver = (0, import_react.useMemo)(function() {
		if (typeof ResizeObserver === "undefined") return null;
		var observer = new ResizeObserver(function(entries) {
			updateNodeDimensions(entries.map(function(entry) {
				return {
					id: entry.target.getAttribute("data-id"),
					nodeElement: entry.target,
					forceUpdate: true
				};
			}));
		});
		resizeObserverRef.current = observer;
		return observer;
	}, []);
	(0, import_react.useEffect)(function() {
		return function() {
			var _resizeObserverRef$cu;
			resizeObserverRef === null || resizeObserverRef === void 0 || (_resizeObserverRef$cu = resizeObserverRef.current) == null || _resizeObserverRef$cu.disconnect();
		};
	}, []);
	return /* @__PURE__ */ import_react.createElement("div", { className: "react-flow__nodes react-flow__container" }, nodes.map(function(node) {
		var _node$positionAbsolut, _node$positionAbsolut2, _node$positionAbsolut3, _node$positionAbsolut4, _node$internalsSymbol, _node$internalsSymbol2, _node$internalsSymbol3;
		var nodeType = node.type || "default";
		if (!props.nodeTypes[nodeType]) {
			console.warn("[React Flow]: Node type \"".concat(nodeType, "\" not found. Using fallback type \"default\". Help: https://reactflow.dev/error#300"));
			nodeType = "default";
		}
		var NodeComponent = props.nodeTypes[nodeType] || props.nodeTypes["default"];
		var isDraggable = !!(node.draggable || nodesDraggable && typeof node.draggable === "undefined");
		var isSelectable = !!(node.selectable || elementsSelectable && typeof node.selectable === "undefined");
		var isConnectable = !!(node.connectable || nodesConnectable && typeof node.connectable === "undefined");
		return /* @__PURE__ */ import_react.createElement(NodeComponent, {
			key: node.id,
			id: node.id,
			className: node.className,
			style: node.style,
			type: nodeType,
			data: node.data,
			sourcePosition: node.sourcePosition || Position.Bottom,
			targetPosition: node.targetPosition || Position.Top,
			hidden: node.hidden,
			xPos: (_node$positionAbsolut = (_node$positionAbsolut2 = node.positionAbsolute) === null || _node$positionAbsolut2 === void 0 ? void 0 : _node$positionAbsolut2.x) !== null && _node$positionAbsolut !== void 0 ? _node$positionAbsolut : 0,
			yPos: (_node$positionAbsolut3 = (_node$positionAbsolut4 = node.positionAbsolute) === null || _node$positionAbsolut4 === void 0 ? void 0 : _node$positionAbsolut4.y) !== null && _node$positionAbsolut3 !== void 0 ? _node$positionAbsolut3 : 0,
			selectNodesOnDrag: props.selectNodesOnDrag,
			onClick: props.onNodeClick,
			onMouseEnter: props.onNodeMouseEnter,
			onMouseMove: props.onNodeMouseMove,
			onMouseLeave: props.onNodeMouseLeave,
			onContextMenu: props.onNodeContextMenu,
			onDoubleClick: props.onNodeDoubleClick,
			selected: !!node.selected,
			isDraggable,
			isSelectable,
			isConnectable,
			resizeObserver,
			dragHandle: node.dragHandle,
			zIndex: (_node$internalsSymbol = (_node$internalsSymbol2 = node[internalsSymbol]) === null || _node$internalsSymbol2 === void 0 ? void 0 : _node$internalsSymbol2.z) !== null && _node$internalsSymbol !== void 0 ? _node$internalsSymbol : 0,
			isParent: !!((_node$internalsSymbol3 = node[internalsSymbol]) !== null && _node$internalsSymbol3 !== void 0 && _node$internalsSymbol3.isParent),
			noDragClassName: props.noDragClassName,
			noPanClassName: props.noPanClassName,
			initialized: !!node.width && !!node.height
		});
	}));
};
NodeRenderer.displayName = "NodeRenderer";
var NodeRenderer$1 = /* @__PURE__ */ (0, import_react.memo)(NodeRenderer);
var _oppositePosition;
function ownKeys$4(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$4(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$4(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$4(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var oppositePosition = (_oppositePosition = {}, _defineProperty(_oppositePosition, Position.Left, Position.Right), _defineProperty(_oppositePosition, Position.Right, Position.Left), _defineProperty(_oppositePosition, Position.Top, Position.Bottom), _defineProperty(_oppositePosition, Position.Bottom, Position.Top), _oppositePosition);
var ConnectionLine = (function(_ref) {
	var _fromNode$internalsSy, _fromNode$width, _fromNode$height, _fromNode$positionAbs, _fromNode$positionAbs2;
	var connectionNodeId = _ref.connectionNodeId, connectionHandleType = _ref.connectionHandleType, connectionLineStyle = _ref.connectionLineStyle, _ref$connectionLineTy = _ref.connectionLineType, connectionLineType = _ref$connectionLineTy === void 0 ? ConnectionLineType.Bezier : _ref$connectionLineTy, isConnectable = _ref.isConnectable, CustomConnectionLineComponent = _ref.CustomConnectionLineComponent;
	var _useStore = useStore((0, import_react.useCallback)(function(s) {
		return {
			fromNode: s.nodeInternals.get(connectionNodeId),
			handleId: s.connectionHandleId,
			toX: (s.connectionPosition.x - s.transform[0]) / s.transform[2],
			toY: (s.connectionPosition.y - s.transform[1]) / s.transform[2]
		};
	}, [connectionNodeId]), shallow), fromNode = _useStore.fromNode, handleId = _useStore.handleId, toX = _useStore.toX, toY = _useStore.toY;
	var fromHandleBounds = fromNode === null || fromNode === void 0 ? void 0 : (_fromNode$internalsSy = fromNode[internalsSymbol]) === null || _fromNode$internalsSy === void 0 ? void 0 : _fromNode$internalsSy.handleBounds;
	if (!fromNode || !isConnectable || !(fromHandleBounds !== null && fromHandleBounds !== void 0 && fromHandleBounds[connectionHandleType])) return null;
	var handleBound = fromHandleBounds[connectionHandleType];
	var fromHandle = handleId ? handleBound.find(function(d) {
		return d.id === handleId;
	}) : handleBound[0];
	var fromHandleX = fromHandle ? fromHandle.x + fromHandle.width / 2 : ((_fromNode$width = fromNode === null || fromNode === void 0 ? void 0 : fromNode.width) !== null && _fromNode$width !== void 0 ? _fromNode$width : 0) / 2;
	var fromHandleY = fromHandle ? fromHandle.y + fromHandle.height / 2 : (_fromNode$height = fromNode === null || fromNode === void 0 ? void 0 : fromNode.height) !== null && _fromNode$height !== void 0 ? _fromNode$height : 0;
	var fromX = ((fromNode === null || fromNode === void 0 ? void 0 : (_fromNode$positionAbs = fromNode.positionAbsolute) === null || _fromNode$positionAbs === void 0 ? void 0 : _fromNode$positionAbs.x) || 0) + fromHandleX;
	var fromY = ((fromNode === null || fromNode === void 0 ? void 0 : (_fromNode$positionAbs2 = fromNode.positionAbsolute) === null || _fromNode$positionAbs2 === void 0 ? void 0 : _fromNode$positionAbs2.y) || 0) + fromHandleY;
	var fromPosition = fromHandle === null || fromHandle === void 0 ? void 0 : fromHandle.position;
	if (!fromPosition) return null;
	var toPosition = oppositePosition[fromPosition];
	var sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition;
	switch (connectionHandleType) {
		case "source":
			sourceX = fromX;
			sourceY = fromY;
			sourcePosition = fromPosition;
			targetX = toX;
			targetY = toY;
			targetPosition = toPosition;
			break;
		case "target":
			sourceX = toX;
			sourceY = toY;
			sourcePosition = toPosition;
			targetX = fromX;
			targetY = fromY;
			targetPosition = fromPosition;
			break;
	}
	if (CustomConnectionLineComponent) return /* @__PURE__ */ import_react.createElement("g", { className: "react-flow__connection" }, /* @__PURE__ */ import_react.createElement(CustomConnectionLineComponent, {
		connectionLineType,
		connectionLineStyle,
		fromNode,
		fromHandle,
		fromX,
		fromY,
		toX,
		toY,
		fromPosition,
		toPosition,
		sourcePosition,
		targetPosition,
		sourceNode: fromNode,
		sourceHandle: fromHandle,
		targetX,
		targetY,
		sourceX,
		sourceY
	}));
	var dAttr = "";
	var pathParams = {
		sourceX,
		sourceY,
		sourcePosition,
		targetX,
		targetY,
		targetPosition
	};
	if (connectionLineType === ConnectionLineType.Bezier) dAttr = getBezierPath(pathParams);
	else if (connectionLineType === ConnectionLineType.Step) dAttr = getSmoothStepPath(_objectSpread$4(_objectSpread$4({}, pathParams), {}, { borderRadius: 0 }));
	else if (connectionLineType === ConnectionLineType.SmoothStep) dAttr = getSmoothStepPath(pathParams);
	else if (connectionLineType === ConnectionLineType.SimpleBezier) dAttr = getSimpleBezierPath(pathParams);
	else dAttr = "M".concat(sourceX, ",").concat(sourceY, " ").concat(targetX, ",").concat(targetY);
	return /* @__PURE__ */ import_react.createElement("g", { className: "react-flow__connection" }, /* @__PURE__ */ import_react.createElement("path", {
		d: dAttr,
		className: "react-flow__connection-path",
		style: connectionLineStyle
	}));
});
function _typeof(obj) {
	"@babel/helpers - typeof";
	return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function(obj) {
		return typeof obj;
	} : function(obj) {
		return obj && "function" == typeof Symbol && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj;
	}, _typeof(obj);
}
var _MarkerSymbols;
var MarkerSymbols = (_MarkerSymbols = {}, _defineProperty(_MarkerSymbols, MarkerType.Arrow, function ArrowSymbol(_ref) {
	var _ref$color = _ref.color, color = _ref$color === void 0 ? "none" : _ref$color, _ref$strokeWidth = _ref.strokeWidth, strokeWidth = _ref$strokeWidth === void 0 ? 1 : _ref$strokeWidth;
	return /* @__PURE__ */ import_react.createElement("polyline", {
		stroke: color,
		strokeLinecap: "round",
		strokeLinejoin: "round",
		strokeWidth,
		fill: "none",
		points: "-5,-4 0,0 -5,4"
	});
}), _defineProperty(_MarkerSymbols, MarkerType.ArrowClosed, function ArrowClosedSymbol(_ref2) {
	var _ref2$color = _ref2.color, color = _ref2$color === void 0 ? "none" : _ref2$color, _ref2$strokeWidth = _ref2.strokeWidth, strokeWidth = _ref2$strokeWidth === void 0 ? 1 : _ref2$strokeWidth;
	return /* @__PURE__ */ import_react.createElement("polyline", {
		stroke: color,
		strokeLinecap: "round",
		strokeLinejoin: "round",
		strokeWidth,
		fill: color,
		points: "-5,-4 0,0 -5,4 -5,-4"
	});
}), _MarkerSymbols);
function useMarkerSymbol(type) {
	return (0, import_react.useMemo)(function() {
		if (!MarkerSymbols.hasOwnProperty(type)) {
			console.warn("[React Flow]: Marker type \"".concat(type, "\" doesn't exist. Help: https://reactflow.dev/error#900"));
			return function() {
				return null;
			};
		}
		return MarkerSymbols[type];
	}, [type]);
}
function ownKeys$3(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$3(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$3(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$3(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var Marker = function Marker(_ref) {
	var id = _ref.id, type = _ref.type, color = _ref.color, _ref$width = _ref.width, width = _ref$width === void 0 ? 12.5 : _ref$width, _ref$height = _ref.height, height = _ref$height === void 0 ? 12.5 : _ref$height, _ref$markerUnits = _ref.markerUnits, markerUnits = _ref$markerUnits === void 0 ? "strokeWidth" : _ref$markerUnits, strokeWidth = _ref.strokeWidth, _ref$orient = _ref.orient, orient = _ref$orient === void 0 ? "auto" : _ref$orient;
	var _Symbol = useMarkerSymbol(type);
	return /* @__PURE__ */ import_react.createElement("marker", {
		className: "react-flow__arrowhead",
		id,
		markerWidth: "".concat(width),
		markerHeight: "".concat(height),
		viewBox: "-10 -10 20 20",
		markerUnits,
		orient,
		refX: "0",
		refY: "0"
	}, /* @__PURE__ */ import_react.createElement(_Symbol, {
		color,
		strokeWidth
	}));
};
var markerSelector = function markerSelector(_ref2) {
	var defaultColor = _ref2.defaultColor, rfId = _ref2.rfId;
	return function(s) {
		var ids = [];
		return s.edges.reduce(function(markers, edge) {
			[edge.markerStart, edge.markerEnd].forEach(function(marker) {
				if (marker && _typeof(marker) === "object") {
					var markerId = getMarkerId(marker, rfId);
					if (!ids.includes(markerId)) {
						markers.push(_objectSpread$3({
							id: markerId,
							color: marker.color || defaultColor
						}, marker));
						ids.push(markerId);
					}
				}
			});
			return markers;
		}, []).sort(function(a, b) {
			return a.id.localeCompare(b.id);
		});
	};
};
var MarkerDefinitions = function MarkerDefinitions(_ref3) {
	var defaultColor = _ref3.defaultColor, rfId = _ref3.rfId;
	var markers = useStore((0, import_react.useCallback)(markerSelector({
		defaultColor,
		rfId
	}), [defaultColor, rfId]), function(a, b) {
		return !(a.length !== b.length || a.some(function(m, i) {
			return m.id !== b[i].id;
		}));
	});
	return /* @__PURE__ */ import_react.createElement("defs", null, markers.map(function(marker) {
		return /* @__PURE__ */ import_react.createElement(Marker, {
			id: marker.id,
			key: marker.id,
			type: marker.type,
			color: marker.color,
			width: marker.width,
			height: marker.height,
			markerUnits: marker.markerUnits,
			strokeWidth: marker.strokeWidth,
			orient: marker.orient
		});
	}));
};
MarkerDefinitions.displayName = "MarkerDefinitions";
var MarkerDefinitions$1 = /* @__PURE__ */ (0, import_react.memo)(MarkerDefinitions);
var defaultEdgeTree = [{
	level: 0,
	isMaxLevel: true,
	edges: []
}];
function groupEdgesByZLevel(edges, nodeInternals) {
	var elevateEdgesOnSelect = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : false;
	var maxLevel = -1;
	var levelLookup = edges.reduce(function(tree, edge) {
		var hasZIndex = isNumeric(edge.zIndex);
		var z = hasZIndex ? edge.zIndex : 0;
		if (elevateEdgesOnSelect) {
			var _nodeInternals$get, _nodeInternals$get$in, _nodeInternals$get2, _nodeInternals$get2$i;
			z = hasZIndex ? edge.zIndex : Math.max(((_nodeInternals$get = nodeInternals.get(edge.source)) === null || _nodeInternals$get === void 0 ? void 0 : (_nodeInternals$get$in = _nodeInternals$get[internalsSymbol]) === null || _nodeInternals$get$in === void 0 ? void 0 : _nodeInternals$get$in.z) || 0, ((_nodeInternals$get2 = nodeInternals.get(edge.target)) === null || _nodeInternals$get2 === void 0 ? void 0 : (_nodeInternals$get2$i = _nodeInternals$get2[internalsSymbol]) === null || _nodeInternals$get2$i === void 0 ? void 0 : _nodeInternals$get2$i.z) || 0);
		}
		if (tree[z]) tree[z].push(edge);
		else tree[z] = [edge];
		maxLevel = z > maxLevel ? z : maxLevel;
		return tree;
	}, {});
	var edgeTree = Object.entries(levelLookup).map(function(_ref) {
		var _ref2 = _slicedToArray(_ref, 2), key = _ref2[0], edges = _ref2[1];
		var level = +key;
		return {
			edges,
			level,
			isMaxLevel: level === maxLevel
		};
	});
	if (edgeTree.length === 0) return defaultEdgeTree;
	return edgeTree;
}
function useVisibleEdges(onlyRenderVisible, nodeInternals, elevateEdgesOnSelect) {
	return groupEdgesByZLevel(useStore((0, import_react.useCallback)(function(s) {
		if (!onlyRenderVisible) return s.edges;
		return s.edges.filter(function(e) {
			var sourceNode = nodeInternals.get(e.source);
			var targetNode = nodeInternals.get(e.target);
			return (sourceNode === null || sourceNode === void 0 ? void 0 : sourceNode.width) && (sourceNode === null || sourceNode === void 0 ? void 0 : sourceNode.height) && (targetNode === null || targetNode === void 0 ? void 0 : targetNode.width) && (targetNode === null || targetNode === void 0 ? void 0 : targetNode.height) && isEdgeVisible({
				sourcePos: sourceNode.positionAbsolute || {
					x: 0,
					y: 0
				},
				targetPos: targetNode.positionAbsolute || {
					x: 0,
					y: 0
				},
				sourceWidth: sourceNode.width,
				sourceHeight: sourceNode.height,
				targetWidth: targetNode.width,
				targetHeight: targetNode.height,
				width: s.width,
				height: s.height,
				transform: s.transform
			});
		});
	}, [onlyRenderVisible, nodeInternals])), nodeInternals, elevateEdgesOnSelect);
}
var selector$1 = function selector(s) {
	return {
		connectionNodeId: s.connectionNodeId,
		connectionHandleType: s.connectionHandleType,
		nodesConnectable: s.nodesConnectable,
		elementsSelectable: s.elementsSelectable,
		width: s.width,
		height: s.height,
		connectionMode: s.connectionMode,
		nodeInternals: s.nodeInternals
	};
};
var EdgeRenderer = function EdgeRenderer(props) {
	var _useStore = useStore(selector$1, shallow), connectionNodeId = _useStore.connectionNodeId, connectionHandleType = _useStore.connectionHandleType, nodesConnectable = _useStore.nodesConnectable, elementsSelectable = _useStore.elementsSelectable, width = _useStore.width, height = _useStore.height, connectionMode = _useStore.connectionMode, nodeInternals = _useStore.nodeInternals;
	var edgeTree = useVisibleEdges(props.onlyRenderVisibleElements, nodeInternals, props.elevateEdgesOnSelect);
	if (!width) return null;
	var connectionLineType = props.connectionLineType, defaultMarkerColor = props.defaultMarkerColor, connectionLineStyle = props.connectionLineStyle, connectionLineComponent = props.connectionLineComponent, connectionLineContainerStyle = props.connectionLineContainerStyle;
	var renderConnectionLine = connectionNodeId && connectionHandleType;
	return /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, edgeTree.map(function(_ref) {
		var level = _ref.level, edges = _ref.edges, isMaxLevel = _ref.isMaxLevel;
		return /* @__PURE__ */ import_react.createElement("svg", {
			key: level,
			style: { zIndex: level },
			width,
			height,
			className: "react-flow__edges react-flow__container"
		}, isMaxLevel && /* @__PURE__ */ import_react.createElement(MarkerDefinitions$1, {
			defaultColor: defaultMarkerColor,
			rfId: props.rfId
		}), /* @__PURE__ */ import_react.createElement("g", null, edges.map(function(edge) {
			var _getNodeData2 = _slicedToArray(getNodeData(nodeInternals, edge.source), 3), sourceNodeRect = _getNodeData2[0], sourceHandleBounds = _getNodeData2[1], sourceIsValid = _getNodeData2[2];
			var _getNodeData4 = _slicedToArray(getNodeData(nodeInternals, edge.target), 3), targetNodeRect = _getNodeData4[0], targetHandleBounds = _getNodeData4[1], targetIsValid = _getNodeData4[2];
			if (!sourceIsValid || !targetIsValid) return null;
			var edgeType = edge.type || "default";
			if (!props.edgeTypes[edgeType]) {
				console.warn("[React Flow]: Edge type \"".concat(edgeType, "\" not found. Using fallback type \"default\". Help: https://reactflow.dev/error#300"));
				edgeType = "default";
			}
			var EdgeComponent = props.edgeTypes[edgeType] || props.edgeTypes["default"];
			var targetNodeHandles = connectionMode === ConnectionMode.Strict ? targetHandleBounds.target : targetHandleBounds.target || targetHandleBounds.source;
			var sourceHandle = getHandle(sourceHandleBounds.source, edge.sourceHandle || null);
			var targetHandle = getHandle(targetNodeHandles, edge.targetHandle || null);
			var sourcePosition = (sourceHandle === null || sourceHandle === void 0 ? void 0 : sourceHandle.position) || Position.Bottom;
			var targetPosition = (targetHandle === null || targetHandle === void 0 ? void 0 : targetHandle.position) || Position.Top;
			if (!sourceHandle) {
				console.warn("[React Flow]: Couldn't create edge for source handle id: ".concat(edge.sourceHandle, "; edge id: ").concat(edge.id, ". Help: https://reactflow.dev/error#800"));
				return null;
			}
			if (!targetHandle) {
				console.warn("[React Flow]: Couldn't create edge for target handle id: ".concat(edge.targetHandle, "; edge id: ").concat(edge.id, ". Help: https://reactflow.dev/error#800"));
				return null;
			}
			var _getEdgePositions = getEdgePositions(sourceNodeRect, sourceHandle, sourcePosition, targetNodeRect, targetHandle, targetPosition), sourceX = _getEdgePositions.sourceX, sourceY = _getEdgePositions.sourceY, targetX = _getEdgePositions.targetX, targetY = _getEdgePositions.targetY;
			return /* @__PURE__ */ import_react.createElement(EdgeComponent, {
				key: edge.id,
				id: edge.id,
				className: cc([edge.className, props.noPanClassName]),
				type: edgeType,
				data: edge.data,
				selected: !!edge.selected,
				animated: !!edge.animated,
				hidden: !!edge.hidden,
				label: edge.label,
				labelStyle: edge.labelStyle,
				labelShowBg: edge.labelShowBg,
				labelBgStyle: edge.labelBgStyle,
				labelBgPadding: edge.labelBgPadding,
				labelBgBorderRadius: edge.labelBgBorderRadius,
				style: edge.style,
				source: edge.source,
				target: edge.target,
				sourceHandleId: edge.sourceHandle,
				targetHandleId: edge.targetHandle,
				markerEnd: edge.markerEnd,
				markerStart: edge.markerStart,
				sourceX,
				sourceY,
				targetX,
				targetY,
				sourcePosition,
				targetPosition,
				elementsSelectable,
				onEdgeUpdate: props.onEdgeUpdate,
				onContextMenu: props.onEdgeContextMenu,
				onMouseEnter: props.onEdgeMouseEnter,
				onMouseMove: props.onEdgeMouseMove,
				onMouseLeave: props.onEdgeMouseLeave,
				onClick: props.onEdgeClick,
				edgeUpdaterRadius: props.edgeUpdaterRadius,
				onEdgeDoubleClick: props.onEdgeDoubleClick,
				onEdgeUpdateStart: props.onEdgeUpdateStart,
				onEdgeUpdateEnd: props.onEdgeUpdateEnd,
				rfId: props.rfId
			});
		})));
	}), renderConnectionLine && /* @__PURE__ */ import_react.createElement("svg", {
		style: connectionLineContainerStyle,
		width,
		height,
		className: "react-flow__edges react-flow__connectionline react-flow__container"
	}, /* @__PURE__ */ import_react.createElement(ConnectionLine, {
		connectionNodeId,
		connectionHandleType,
		connectionLineStyle,
		connectionLineType,
		isConnectable: nodesConnectable,
		CustomConnectionLineComponent: connectionLineComponent
	})));
};
EdgeRenderer.displayName = "EdgeRenderer";
var EdgeRenderer$1 = /* @__PURE__ */ (0, import_react.memo)(EdgeRenderer);
var selector = function selector(s) {
	return "translate(".concat(s.transform[0], "px,").concat(s.transform[1], "px) scale(").concat(s.transform[2], ")");
};
function Viewport(_ref) {
	var children = _ref.children;
	var transform = useStore(selector);
	return /* @__PURE__ */ import_react.createElement("div", {
		className: "react-flow__viewport react-flow__container",
		style: { transform }
	}, children);
}
function useOnInitHandler(onInit) {
	var ReactFlowInstance = useReactFlow();
	var isInitialized = (0, import_react.useRef)(false);
	(0, import_react.useEffect)(function() {
		if (!isInitialized.current && ReactFlowInstance.viewportInitialized && onInit) {
			setTimeout(function() {
				return onInit(ReactFlowInstance);
			}, 1);
			isInitialized.current = true;
		}
	}, [onInit, ReactFlowInstance.viewportInitialized]);
}
var GraphView = function GraphView(_ref) {
	var nodeTypes = _ref.nodeTypes, edgeTypes = _ref.edgeTypes, onMove = _ref.onMove, onMoveStart = _ref.onMoveStart, onMoveEnd = _ref.onMoveEnd, onInit = _ref.onInit, onNodeClick = _ref.onNodeClick, onEdgeClick = _ref.onEdgeClick, onNodeDoubleClick = _ref.onNodeDoubleClick, onEdgeDoubleClick = _ref.onEdgeDoubleClick, onNodeMouseEnter = _ref.onNodeMouseEnter, onNodeMouseMove = _ref.onNodeMouseMove, onNodeMouseLeave = _ref.onNodeMouseLeave, onNodeContextMenu = _ref.onNodeContextMenu, onSelectionContextMenu = _ref.onSelectionContextMenu, connectionLineType = _ref.connectionLineType, connectionLineStyle = _ref.connectionLineStyle, connectionLineComponent = _ref.connectionLineComponent, connectionLineContainerStyle = _ref.connectionLineContainerStyle, selectionKeyCode = _ref.selectionKeyCode, multiSelectionKeyCode = _ref.multiSelectionKeyCode, zoomActivationKeyCode = _ref.zoomActivationKeyCode, deleteKeyCode = _ref.deleteKeyCode, onlyRenderVisibleElements = _ref.onlyRenderVisibleElements, elementsSelectable = _ref.elementsSelectable, selectNodesOnDrag = _ref.selectNodesOnDrag, translateExtent = _ref.translateExtent, minZoom = _ref.minZoom, maxZoom = _ref.maxZoom, defaultZoom = _ref.defaultZoom, defaultPosition = _ref.defaultPosition, preventScrolling = _ref.preventScrolling, defaultMarkerColor = _ref.defaultMarkerColor, zoomOnScroll = _ref.zoomOnScroll, zoomOnPinch = _ref.zoomOnPinch, panOnScroll = _ref.panOnScroll, panOnScrollSpeed = _ref.panOnScrollSpeed, panOnScrollMode = _ref.panOnScrollMode, zoomOnDoubleClick = _ref.zoomOnDoubleClick, panOnDrag = _ref.panOnDrag, onPaneClick = _ref.onPaneClick, onPaneScroll = _ref.onPaneScroll, onPaneContextMenu = _ref.onPaneContextMenu, onEdgeUpdate = _ref.onEdgeUpdate, onEdgeContextMenu = _ref.onEdgeContextMenu, onEdgeMouseEnter = _ref.onEdgeMouseEnter, onEdgeMouseMove = _ref.onEdgeMouseMove, onEdgeMouseLeave = _ref.onEdgeMouseLeave, edgeUpdaterRadius = _ref.edgeUpdaterRadius, onEdgeUpdateStart = _ref.onEdgeUpdateStart, onEdgeUpdateEnd = _ref.onEdgeUpdateEnd, noDragClassName = _ref.noDragClassName, noWheelClassName = _ref.noWheelClassName, noPanClassName = _ref.noPanClassName, elevateEdgesOnSelect = _ref.elevateEdgesOnSelect, id = _ref.id;
	useOnInitHandler(onInit);
	return /* @__PURE__ */ import_react.createElement(FlowRenderer$1, {
		onPaneClick,
		onPaneContextMenu,
		onPaneScroll,
		deleteKeyCode,
		selectionKeyCode,
		multiSelectionKeyCode,
		zoomActivationKeyCode,
		elementsSelectable,
		onMove,
		onMoveStart,
		onMoveEnd,
		zoomOnScroll,
		zoomOnPinch,
		zoomOnDoubleClick,
		panOnScroll,
		panOnScrollSpeed,
		panOnScrollMode,
		panOnDrag,
		translateExtent,
		minZoom,
		maxZoom,
		defaultZoom,
		defaultPosition,
		onSelectionContextMenu,
		preventScrolling,
		noDragClassName,
		noWheelClassName,
		noPanClassName
	}, /* @__PURE__ */ import_react.createElement(Viewport, null, /* @__PURE__ */ import_react.createElement(EdgeRenderer$1, {
		edgeTypes,
		onEdgeClick,
		onEdgeDoubleClick,
		connectionLineType,
		connectionLineStyle,
		connectionLineComponent,
		connectionLineContainerStyle,
		onEdgeUpdate,
		onlyRenderVisibleElements,
		onEdgeContextMenu,
		onEdgeMouseEnter,
		onEdgeMouseMove,
		onEdgeMouseLeave,
		onEdgeUpdateStart,
		onEdgeUpdateEnd,
		edgeUpdaterRadius,
		defaultMarkerColor,
		noPanClassName,
		elevateEdgesOnSelect: !!elevateEdgesOnSelect,
		rfId: id
	}), /* @__PURE__ */ import_react.createElement(NodeRenderer$1, {
		nodeTypes,
		onNodeClick,
		onNodeDoubleClick,
		onNodeMouseEnter,
		onNodeMouseMove,
		onNodeMouseLeave,
		onNodeContextMenu,
		selectNodesOnDrag,
		onlyRenderVisibleElements,
		noPanClassName,
		noDragClassName
	})));
};
GraphView.displayName = "GraphView";
var GraphView$1 = /* @__PURE__ */ (0, import_react.memo)(GraphView);
var GroupNode = function GroupNode() {
	return null;
};
GroupNode.displayName = "GroupNode";
function ownKeys$2(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$2(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$2(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$2(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
var wrapNode = (function(NodeComponent) {
	var NodeWrapper = function NodeWrapper(_ref) {
		var id = _ref.id, type = _ref.type, data = _ref.data, xPos = _ref.xPos, yPos = _ref.yPos, selected = _ref.selected, onClick = _ref.onClick, onMouseEnter = _ref.onMouseEnter, onMouseMove = _ref.onMouseMove, onMouseLeave = _ref.onMouseLeave, onContextMenu = _ref.onContextMenu, onDoubleClick = _ref.onDoubleClick, style = _ref.style, className = _ref.className, isDraggable = _ref.isDraggable, isSelectable = _ref.isSelectable, isConnectable = _ref.isConnectable, selectNodesOnDrag = _ref.selectNodesOnDrag, sourcePosition = _ref.sourcePosition, targetPosition = _ref.targetPosition, hidden = _ref.hidden, resizeObserver = _ref.resizeObserver, dragHandle = _ref.dragHandle, zIndex = _ref.zIndex, isParent = _ref.isParent, noPanClassName = _ref.noPanClassName, noDragClassName = _ref.noDragClassName, initialized = _ref.initialized;
		var store = useStoreApi();
		var nodeRef = (0, import_react.useRef)(null);
		var prevSourcePosition = (0, import_react.useRef)(sourcePosition);
		var prevTargetPosition = (0, import_react.useRef)(targetPosition);
		var prevType = (0, import_react.useRef)(type);
		var hasPointerEvents = isSelectable || isDraggable || onClick || onMouseEnter || onMouseMove || onMouseLeave;
		var onMouseEnterHandler = getMouseHandler$1(id, store.getState, onMouseEnter);
		var onMouseMoveHandler = getMouseHandler$1(id, store.getState, onMouseMove);
		var onMouseLeaveHandler = getMouseHandler$1(id, store.getState, onMouseLeave);
		var onContextMenuHandler = getMouseHandler$1(id, store.getState, onContextMenu);
		var onDoubleClickHandler = getMouseHandler$1(id, store.getState, onDoubleClick);
		var onSelectNodeHandler = function onSelectNodeHandler(event) {
			if (isSelectable && (!selectNodesOnDrag || !isDraggable)) handleNodeClick({
				id,
				store
			});
			if (onClick) onClick(event, _objectSpread$2({}, store.getState().nodeInternals.get(id)));
		};
		(0, import_react.useEffect)(function() {
			if (nodeRef.current && !hidden) {
				var currNode = nodeRef.current;
				resizeObserver === null || resizeObserver === void 0 || resizeObserver.observe(currNode);
				return function() {
					return resizeObserver === null || resizeObserver === void 0 ? void 0 : resizeObserver.unobserve(currNode);
				};
			}
		}, [hidden]);
		(0, import_react.useEffect)(function() {
			var typeChanged = prevType.current !== type;
			var sourcePosChanged = prevSourcePosition.current !== sourcePosition;
			var targetPosChanged = prevTargetPosition.current !== targetPosition;
			if (nodeRef.current && (typeChanged || sourcePosChanged || targetPosChanged)) {
				if (typeChanged) prevType.current = type;
				if (sourcePosChanged) prevSourcePosition.current = sourcePosition;
				if (targetPosChanged) prevTargetPosition.current = targetPosition;
				store.getState().updateNodeDimensions([{
					id,
					nodeElement: nodeRef.current,
					forceUpdate: true
				}]);
			}
		}, [
			id,
			type,
			sourcePosition,
			targetPosition
		]);
		var dragging = useDrag({
			nodeRef,
			disabled: hidden || !isDraggable,
			noDragClassName,
			handleSelector: dragHandle,
			nodeId: id,
			isSelectable,
			selectNodesOnDrag
		});
		if (hidden) return null;
		return /* @__PURE__ */ import_react.createElement("div", {
			className: cc([
				"react-flow__node",
				"react-flow__node-".concat(type),
				noPanClassName,
				className,
				{
					selected,
					selectable: isSelectable,
					parent: isParent
				}
			]),
			ref: nodeRef,
			style: _objectSpread$2({
				zIndex,
				transform: "translate(".concat(xPos, "px,").concat(yPos, "px)"),
				pointerEvents: hasPointerEvents ? "all" : "none",
				visibility: initialized ? "visible" : "hidden"
			}, style),
			onMouseEnter: onMouseEnterHandler,
			onMouseMove: onMouseMoveHandler,
			onMouseLeave: onMouseLeaveHandler,
			onContextMenu: onContextMenuHandler,
			onClick: onSelectNodeHandler,
			onDoubleClick: onDoubleClickHandler,
			"data-testid": "rf__node-".concat(id),
			"data-id": id
		}, /* @__PURE__ */ import_react.createElement(Provider, { value: id }, /* @__PURE__ */ import_react.createElement(NodeComponent, {
			id,
			data,
			type,
			xPos,
			yPos,
			selected,
			isConnectable,
			sourcePosition,
			targetPosition,
			dragging,
			dragHandle,
			zIndex
		})));
	};
	NodeWrapper.displayName = "NodeWrapper";
	return /* @__PURE__ */ (0, import_react.memo)(NodeWrapper);
});
function ownKeys$1(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread$1(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys$1(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys$1(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
function createNodeTypes(nodeTypes) {
	var standardTypes = {
		input: wrapNode(nodeTypes.input || InputNode$1),
		"default": wrapNode(nodeTypes["default"] || DefaultNode$1),
		output: wrapNode(nodeTypes.output || OutputNode$1),
		group: wrapNode(nodeTypes.group || GroupNode)
	};
	var specialTypes = Object.keys(nodeTypes).filter(function(k) {
		return ![
			"input",
			"default",
			"output",
			"group"
		].includes(k);
	}).reduce(function(res, key) {
		res[key] = wrapNode(nodeTypes[key] || DefaultNode$1);
		return res;
	}, {});
	return _objectSpread$1(_objectSpread$1({}, standardTypes), specialTypes);
}
function useNodeOrEdgeTypes(nodeOrEdgeTypes, createTypes) {
	var typesKeysRef = (0, import_react.useRef)(null);
	return (0, import_react.useMemo)(function() {
		var typeKeys = Object.keys(nodeOrEdgeTypes);
		if (shallow(typesKeysRef.current, typeKeys)) console.warn("[React Flow]: It looks like you have created a new nodeTypes or edgeTypes object. If this wasn't on purpose please define the nodeTypes/edgeTypes outside of the component or memoize them. Help: https://reactflow.dev/error#200");
		typesKeysRef.current = typeKeys;
		return createTypes(nodeOrEdgeTypes);
	}, [nodeOrEdgeTypes]);
}
function injectStyle(css) {
	if (!css || typeof document === "undefined") return;
	var head = document.head || document.getElementsByTagName("head")[0];
	var style = document.createElement("style");
	head.appendChild(style);
	style.appendChild(document.createTextNode(css));
}
var Wrapper = function Wrapper(_ref) {
	var children = _ref.children;
	var isWrapped = true;
	try {
		useStoreApi();
	} catch (e) {
		isWrapped = false;
	}
	if (isWrapped) return /* @__PURE__ */ import_react.createElement(import_react.Fragment, null, children);
	return /* @__PURE__ */ import_react.createElement(Provider$1, { createStore }, children);
};
Wrapper.displayName = "ReactFlowWrapper";
var _excluded = [
	"nodes",
	"edges",
	"defaultNodes",
	"defaultEdges",
	"className",
	"nodeTypes",
	"edgeTypes",
	"onNodeClick",
	"onEdgeClick",
	"onInit",
	"onMove",
	"onMoveStart",
	"onMoveEnd",
	"onConnect",
	"onConnectStart",
	"onConnectStop",
	"onConnectEnd",
	"onClickConnectStart",
	"onClickConnectStop",
	"onClickConnectEnd",
	"onNodeMouseEnter",
	"onNodeMouseMove",
	"onNodeMouseLeave",
	"onNodeContextMenu",
	"onNodeDoubleClick",
	"onNodeDragStart",
	"onNodeDrag",
	"onNodeDragStop",
	"onNodesDelete",
	"onEdgesDelete",
	"onSelectionChange",
	"onSelectionDragStart",
	"onSelectionDrag",
	"onSelectionDragStop",
	"onSelectionContextMenu",
	"connectionMode",
	"connectionLineType",
	"connectionLineStyle",
	"connectionLineComponent",
	"connectionLineContainerStyle",
	"deleteKeyCode",
	"selectionKeyCode",
	"multiSelectionKeyCode",
	"zoomActivationKeyCode",
	"snapToGrid",
	"snapGrid",
	"onlyRenderVisibleElements",
	"selectNodesOnDrag",
	"nodesDraggable",
	"nodesConnectable",
	"elementsSelectable",
	"minZoom",
	"maxZoom",
	"defaultZoom",
	"defaultPosition",
	"translateExtent",
	"preventScrolling",
	"nodeExtent",
	"defaultMarkerColor",
	"zoomOnScroll",
	"zoomOnPinch",
	"panOnScroll",
	"panOnScrollSpeed",
	"panOnScrollMode",
	"zoomOnDoubleClick",
	"panOnDrag",
	"onPaneClick",
	"onPaneScroll",
	"onPaneContextMenu",
	"children",
	"onEdgeUpdate",
	"onEdgeContextMenu",
	"onEdgeDoubleClick",
	"onEdgeMouseEnter",
	"onEdgeMouseMove",
	"onEdgeMouseLeave",
	"onEdgeUpdateStart",
	"onEdgeUpdateEnd",
	"edgeUpdaterRadius",
	"onNodesChange",
	"onEdgesChange",
	"noDragClassName",
	"noWheelClassName",
	"noPanClassName",
	"fitView",
	"fitViewOptions",
	"connectOnClick",
	"attributionPosition",
	"proOptions",
	"defaultEdgeOptions",
	"elevateEdgesOnSelect"
];
function ownKeys(object, enumerableOnly) {
	var keys = Object.keys(object);
	if (Object.getOwnPropertySymbols) {
		var symbols = Object.getOwnPropertySymbols(object);
		enumerableOnly && (symbols = symbols.filter(function(sym) {
			return Object.getOwnPropertyDescriptor(object, sym).enumerable;
		})), keys.push.apply(keys, symbols);
	}
	return keys;
}
function _objectSpread(target) {
	for (var i = 1; i < arguments.length; i++) {
		var source = null != arguments[i] ? arguments[i] : {};
		i % 2 ? ownKeys(Object(source), !0).forEach(function(key) {
			_defineProperty(target, key, source[key]);
		}) : Object.getOwnPropertyDescriptors ? Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)) : ownKeys(Object(source)).forEach(function(key) {
			Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
		});
	}
	return target;
}
injectStyle(css);
injectStyle(theme);
var defaultNodeTypes = {
	input: InputNode$1,
	"default": DefaultNode$1,
	output: OutputNode$1
};
var defaultEdgeTypes = {
	"default": BezierEdge,
	straight: StraightEdge,
	step: StepEdge,
	smoothstep: SmoothStepEdge,
	simplebezier: SimpleBezierEdge
};
var initSnapGrid = [15, 15];
var initDefaultPosition = [0, 0];
var ReactFlow = /* @__PURE__ */ (0, import_react.forwardRef)(function(_ref, ref) {
	var nodes = _ref.nodes, edges = _ref.edges, defaultNodes = _ref.defaultNodes, defaultEdges = _ref.defaultEdges, className = _ref.className, _ref$nodeTypes = _ref.nodeTypes, nodeTypes = _ref$nodeTypes === void 0 ? defaultNodeTypes : _ref$nodeTypes, _ref$edgeTypes = _ref.edgeTypes, edgeTypes = _ref$edgeTypes === void 0 ? defaultEdgeTypes : _ref$edgeTypes, onNodeClick = _ref.onNodeClick, onEdgeClick = _ref.onEdgeClick, onInit = _ref.onInit, onMove = _ref.onMove, onMoveStart = _ref.onMoveStart, onMoveEnd = _ref.onMoveEnd, onConnect = _ref.onConnect, onConnectStart = _ref.onConnectStart, onConnectStop = _ref.onConnectStop, onConnectEnd = _ref.onConnectEnd, onClickConnectStart = _ref.onClickConnectStart, onClickConnectStop = _ref.onClickConnectStop, onClickConnectEnd = _ref.onClickConnectEnd, onNodeMouseEnter = _ref.onNodeMouseEnter, onNodeMouseMove = _ref.onNodeMouseMove, onNodeMouseLeave = _ref.onNodeMouseLeave, onNodeContextMenu = _ref.onNodeContextMenu, onNodeDoubleClick = _ref.onNodeDoubleClick, onNodeDragStart = _ref.onNodeDragStart, onNodeDrag = _ref.onNodeDrag, onNodeDragStop = _ref.onNodeDragStop, onNodesDelete = _ref.onNodesDelete, onEdgesDelete = _ref.onEdgesDelete, onSelectionChange = _ref.onSelectionChange, onSelectionDragStart = _ref.onSelectionDragStart, onSelectionDrag = _ref.onSelectionDrag, onSelectionDragStop = _ref.onSelectionDragStop, onSelectionContextMenu = _ref.onSelectionContextMenu, _ref$connectionMode = _ref.connectionMode, connectionMode = _ref$connectionMode === void 0 ? ConnectionMode.Strict : _ref$connectionMode, _ref$connectionLineTy = _ref.connectionLineType, connectionLineType = _ref$connectionLineTy === void 0 ? ConnectionLineType.Bezier : _ref$connectionLineTy, connectionLineStyle = _ref.connectionLineStyle, connectionLineComponent = _ref.connectionLineComponent, connectionLineContainerStyle = _ref.connectionLineContainerStyle, _ref$deleteKeyCode = _ref.deleteKeyCode, deleteKeyCode = _ref$deleteKeyCode === void 0 ? "Backspace" : _ref$deleteKeyCode, _ref$selectionKeyCode = _ref.selectionKeyCode, selectionKeyCode = _ref$selectionKeyCode === void 0 ? "Shift" : _ref$selectionKeyCode, _ref$multiSelectionKe = _ref.multiSelectionKeyCode, multiSelectionKeyCode = _ref$multiSelectionKe === void 0 ? "Meta" : _ref$multiSelectionKe, _ref$zoomActivationKe = _ref.zoomActivationKeyCode, zoomActivationKeyCode = _ref$zoomActivationKe === void 0 ? "Meta" : _ref$zoomActivationKe, _ref$snapToGrid = _ref.snapToGrid, snapToGrid = _ref$snapToGrid === void 0 ? false : _ref$snapToGrid, _ref$snapGrid = _ref.snapGrid, snapGrid = _ref$snapGrid === void 0 ? initSnapGrid : _ref$snapGrid, _ref$onlyRenderVisibl = _ref.onlyRenderVisibleElements, onlyRenderVisibleElements = _ref$onlyRenderVisibl === void 0 ? false : _ref$onlyRenderVisibl, _ref$selectNodesOnDra = _ref.selectNodesOnDrag, selectNodesOnDrag = _ref$selectNodesOnDra === void 0 ? true : _ref$selectNodesOnDra, nodesDraggable = _ref.nodesDraggable, nodesConnectable = _ref.nodesConnectable, elementsSelectable = _ref.elementsSelectable, _ref$minZoom = _ref.minZoom, minZoom = _ref$minZoom === void 0 ? .5 : _ref$minZoom, _ref$maxZoom = _ref.maxZoom, maxZoom = _ref$maxZoom === void 0 ? 2 : _ref$maxZoom, _ref$defaultZoom = _ref.defaultZoom, defaultZoom = _ref$defaultZoom === void 0 ? 1 : _ref$defaultZoom, _ref$defaultPosition = _ref.defaultPosition, defaultPosition = _ref$defaultPosition === void 0 ? initDefaultPosition : _ref$defaultPosition, _ref$translateExtent = _ref.translateExtent, translateExtent = _ref$translateExtent === void 0 ? infiniteExtent : _ref$translateExtent, _ref$preventScrolling = _ref.preventScrolling, preventScrolling = _ref$preventScrolling === void 0 ? true : _ref$preventScrolling, nodeExtent = _ref.nodeExtent, _ref$defaultMarkerCol = _ref.defaultMarkerColor, defaultMarkerColor = _ref$defaultMarkerCol === void 0 ? "#b1b1b7" : _ref$defaultMarkerCol, _ref$zoomOnScroll = _ref.zoomOnScroll, zoomOnScroll = _ref$zoomOnScroll === void 0 ? true : _ref$zoomOnScroll, _ref$zoomOnPinch = _ref.zoomOnPinch, zoomOnPinch = _ref$zoomOnPinch === void 0 ? true : _ref$zoomOnPinch, _ref$panOnScroll = _ref.panOnScroll, panOnScroll = _ref$panOnScroll === void 0 ? false : _ref$panOnScroll, _ref$panOnScrollSpeed = _ref.panOnScrollSpeed, panOnScrollSpeed = _ref$panOnScrollSpeed === void 0 ? .5 : _ref$panOnScrollSpeed, _ref$panOnScrollMode = _ref.panOnScrollMode, panOnScrollMode = _ref$panOnScrollMode === void 0 ? PanOnScrollMode.Free : _ref$panOnScrollMode, _ref$zoomOnDoubleClic = _ref.zoomOnDoubleClick, zoomOnDoubleClick = _ref$zoomOnDoubleClic === void 0 ? true : _ref$zoomOnDoubleClic, _ref$panOnDrag = _ref.panOnDrag, panOnDrag = _ref$panOnDrag === void 0 ? true : _ref$panOnDrag, onPaneClick = _ref.onPaneClick, onPaneScroll = _ref.onPaneScroll, onPaneContextMenu = _ref.onPaneContextMenu, children = _ref.children, onEdgeUpdate = _ref.onEdgeUpdate, onEdgeContextMenu = _ref.onEdgeContextMenu, onEdgeDoubleClick = _ref.onEdgeDoubleClick, onEdgeMouseEnter = _ref.onEdgeMouseEnter, onEdgeMouseMove = _ref.onEdgeMouseMove, onEdgeMouseLeave = _ref.onEdgeMouseLeave, onEdgeUpdateStart = _ref.onEdgeUpdateStart, onEdgeUpdateEnd = _ref.onEdgeUpdateEnd, _ref$edgeUpdaterRadiu = _ref.edgeUpdaterRadius, edgeUpdaterRadius = _ref$edgeUpdaterRadiu === void 0 ? 10 : _ref$edgeUpdaterRadiu, onNodesChange = _ref.onNodesChange, onEdgesChange = _ref.onEdgesChange, _ref$noDragClassName = _ref.noDragClassName, noDragClassName = _ref$noDragClassName === void 0 ? "nodrag" : _ref$noDragClassName, _ref$noWheelClassName = _ref.noWheelClassName, noWheelClassName = _ref$noWheelClassName === void 0 ? "nowheel" : _ref$noWheelClassName, _ref$noPanClassName = _ref.noPanClassName, noPanClassName = _ref$noPanClassName === void 0 ? "nopan" : _ref$noPanClassName, _ref$fitView = _ref.fitView, fitView = _ref$fitView === void 0 ? false : _ref$fitView, fitViewOptions = _ref.fitViewOptions, _ref$connectOnClick = _ref.connectOnClick, connectOnClick = _ref$connectOnClick === void 0 ? true : _ref$connectOnClick, attributionPosition = _ref.attributionPosition, proOptions = _ref.proOptions, defaultEdgeOptions = _ref.defaultEdgeOptions, _ref$elevateEdgesOnSe = _ref.elevateEdgesOnSelect, elevateEdgesOnSelect = _ref$elevateEdgesOnSe === void 0 ? false : _ref$elevateEdgesOnSe, rest = _objectWithoutProperties(_ref, _excluded);
	var nodeTypesWrapped = useNodeOrEdgeTypes(nodeTypes, createNodeTypes);
	var edgeTypesWrapped = useNodeOrEdgeTypes(edgeTypes, createEdgeTypes);
	return /* @__PURE__ */ import_react.createElement("div", _objectSpread(_objectSpread({}, rest), {}, {
		ref,
		className: cc(["react-flow", className])
	}), /* @__PURE__ */ import_react.createElement(Wrapper, null, /* @__PURE__ */ import_react.createElement(GraphView$1, {
		onInit,
		onMove,
		onMoveStart,
		onMoveEnd,
		onNodeClick,
		onEdgeClick,
		onNodeMouseEnter,
		onNodeMouseMove,
		onNodeMouseLeave,
		onNodeContextMenu,
		onNodeDoubleClick,
		nodeTypes: nodeTypesWrapped,
		edgeTypes: edgeTypesWrapped,
		connectionLineType,
		connectionLineStyle,
		connectionLineComponent,
		connectionLineContainerStyle,
		selectionKeyCode,
		deleteKeyCode,
		multiSelectionKeyCode,
		zoomActivationKeyCode,
		onlyRenderVisibleElements,
		selectNodesOnDrag,
		translateExtent,
		minZoom,
		maxZoom,
		defaultZoom,
		defaultPosition,
		preventScrolling,
		zoomOnScroll,
		zoomOnPinch,
		zoomOnDoubleClick,
		panOnScroll,
		panOnScrollSpeed,
		panOnScrollMode,
		panOnDrag,
		onPaneClick,
		onPaneScroll,
		onPaneContextMenu,
		onSelectionContextMenu,
		onEdgeUpdate,
		onEdgeContextMenu,
		onEdgeDoubleClick,
		onEdgeMouseEnter,
		onEdgeMouseMove,
		onEdgeMouseLeave,
		onEdgeUpdateStart,
		onEdgeUpdateEnd,
		edgeUpdaterRadius,
		defaultMarkerColor,
		noDragClassName,
		noWheelClassName,
		noPanClassName,
		elevateEdgesOnSelect,
		id: rest === null || rest === void 0 ? void 0 : rest.id
	}), /* @__PURE__ */ import_react.createElement(StoreUpdater, {
		nodes,
		edges,
		defaultNodes,
		defaultEdges,
		onConnect,
		onConnectStart,
		onConnectStop,
		onConnectEnd,
		onClickConnectStart,
		onClickConnectStop,
		onClickConnectEnd,
		nodesDraggable,
		nodesConnectable,
		elementsSelectable,
		minZoom,
		maxZoom,
		nodeExtent,
		onNodesChange,
		onEdgesChange,
		snapToGrid,
		snapGrid,
		connectionMode,
		translateExtent,
		connectOnClick,
		defaultEdgeOptions,
		fitView,
		fitViewOptions,
		onNodesDelete,
		onEdgesDelete,
		onNodeDragStart,
		onNodeDrag,
		onNodeDragStop,
		onSelectionDrag,
		onSelectionDragStart,
		onSelectionDragStop
	}), onSelectionChange && /* @__PURE__ */ import_react.createElement(SelectionListener$1, { onSelectionChange }), children, /* @__PURE__ */ import_react.createElement(Attribution, {
		proOptions,
		position: attributionPosition
	})));
});
ReactFlow.displayName = "ReactFlow";
var ReactFlowProvider = function ReactFlowProvider(_ref) {
	var children = _ref.children;
	return /* @__PURE__ */ import_react.createElement(Provider$1, { createStore }, children);
};
ReactFlowProvider.displayName = "ReactFlowProvider";
function createUseItemsState(applyChanges) {
	return function(initialItems) {
		var _useState2 = _slicedToArray((0, import_react.useState)(initialItems), 2), items = _useState2[0], setItems = _useState2[1];
		return [
			items,
			setItems,
			(0, import_react.useCallback)(function(changes) {
				return setItems(function(items) {
					return applyChanges(changes, items);
				});
			}, [])
		];
	};
}
var useNodesState = createUseItemsState(applyNodeChanges);
var useEdgesState = createUseItemsState(applyEdgeChanges);
//#endregion
export { index as Background, BackgroundVariant, BezierEdge, ConnectionLineType, ConnectionMode, ControlButton, index$1 as Controls, EdgeText$1 as EdgeText, Handle$1 as Handle, MarkerType, index$2 as MiniMap, PanOnScrollMode, Position, ReactFlowProvider, SimpleBezierEdge, SmoothStepEdge, StepEdge, StraightEdge, addEdge, applyEdgeChanges, applyNodeChanges, ReactFlow as default, getBezierCenter as getBezierEdgeCenter, getBezierPath, getConnectedEdges, getCenter as getEdgeCenter, getIncomers, getMarkerEnd, getOutgoers, getRectOfNodes, getSimpleBezierCenter as getSimpleBezierEdgeCenter, getSimpleBezierPath, getSmoothStepPath, getTransformForBounds, internalsSymbol, isEdge, isNode, updateEdge, useEdges, useEdgesState, useKeyPress, useNodes, useNodesState, useReactFlow, useStore, useStoreApi, useUpdateNodeInternals, useViewport };

//# sourceMappingURL=react-flow-renderer.js.map