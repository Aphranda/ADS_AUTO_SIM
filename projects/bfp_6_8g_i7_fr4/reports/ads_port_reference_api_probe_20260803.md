# ADS Python API Probe

Generated: 2026-08-03T00:39:11
Python: `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe`
Keywords: `secondary, reference, ground, gnd, port, term, em`

## Keyword Child Modules

### `keysight.ads.ael`
- `keysight.ads.ael._ael_support`
- `keysight.ads.ael._setup_support`

### `keysight.ads.emtools`
- `keysight.ads.emtools._emtools`
- `keysight.ads.emtools._setup_environment`
- `keysight.ads.emtools._setup_support`

## API Hits

### `keysight.ads.ael`

_No keyword hits._

### `keysight.ads.de.db_uu`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.de.db_uu.ApolloObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ApolloObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.AppObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.AppObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Arc.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Arc.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Arc.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Arc.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ArrayInst.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.ArrayInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ArrayInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.ArrayInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.ArrayInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ArrayInst.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.ArrayInst.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.ArrayInst.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.ArrayInst.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.ArrayInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.ArrayInst.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.ArrayInst.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.ArrayInst.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.ArrayInst.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.ArrayInst.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.AttrDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.AttrDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.AttrDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.AttrDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.BlockObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BlockObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleNet.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BundleNet.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BundleNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleNet.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BundleNet.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm` | class | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A multi-bit term whose name contains commas separating the bits (e.g. "a, b, c"). |
| `keysight.ads.de.db_uu.BundleTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BundleTerm.bits` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BundleTerm.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.BundleTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.BundleTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.BundleTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BundleTerm.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.BundleTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BundleTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.BundleTerm.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.BundleTerm.name` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.BundleTerm.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.BundleTerm.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.BundleTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BundleTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BundleTerm.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.BusNet.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusNet.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusNet.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNet.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.BusNetBit.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusNetBit.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNetBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusNetBit.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNetBit.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm` | class | `(net: keysight.ads.de.db_uu._db_x.Net, base_name: str, start: int, stop: int, step: int = 1, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A multi-bit term whose name uses bus syntax (e.g. "P<0:7>"). |
| `keysight.ads.de.db_uu.BusTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusTerm.bits` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTerm.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.BusTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.BusTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.BusTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BusTerm.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.BusTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.BusTerm.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.BusTerm.name` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.BusTerm.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.BusTerm.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.BusTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BusTerm.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.BusTermBit` | class | `(net: keysight.ads.de.db_uu._db_x.Net, base_name: str, bit: int, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A multi-bit term whose name uses bus syntax (e.g. "P<0:7>"). |
| `keysight.ads.de.db_uu.BusTermBit.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusTermBit.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTermBit.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.BusTermBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTermBit.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.BusTermBit.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.BusTermBit.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BusTermBit.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.BusTermBit.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusTermBit.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.BusTermBit.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.BusTermBit.name` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.net` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.BusTermBit.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.BusTermBit.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.BusTermBit.props` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTermBit.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BusTermBit.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.CompositeObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.CompositeObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CompositeObject.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.CompositeObject.members` | property | `` |  |
| `keysight.ads.de.db_uu.CompoundForm` | class | `(name: str, label: str = '', params: collections.abc.Sequence[keysight.ads.de.db._model_def.ModelParam] = [], net_format: str = '', display_format: str = '', dialog_data: str = '') -> None` | CompoundForm is a type of Form for a parameter that contains one or more sub-parameters. The CompoundForm describes how the parameter is netlisted and displayed. The Form for each sub-parameter describes how that port... |
| `keysight.ads.de.db_uu.CompoundForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.ConnectivityOptions.calculate_flight_lines_between_grounds` | property | `` | True if flight lines are calculated between ground nets. |
| `keysight.ads.de.db_uu.ConstForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.ConstructionLine.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ConstructionLine.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.create_schematic` | function | `(name: 'CellviewRefLike') -> keysight.ads.de.db_uu._design.Design` | Create a schematic from an open library in the active workspace. Parameters ---------- name: CellviewRefLike The name of the design, usually of the form "LibraryName:CellName:schematic" Example ------- >>> design = de... |
| `keysight.ads.de.db_uu.CustomVia` | class | `(design: 'Design', via_def_name: str, origin: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> None` | A custom OpenAccess Via. The via is defined partly by its definition in the technology. The geometry of a custom via is determined by another design. |
| `keysight.ads.de.db_uu.CustomVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.CustomVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CustomVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.CustomVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.CustomVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.CustomVia.via_master_lcv_name` | property | `` | The cellview name of the master design referenced by this custom via. |
| `keysight.ads.de.db_uu.Design.add_numbered_term` | function | `(self, net: 'Net', term_name: str, term_number: int, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>) -> 'Term'` | Add a numbered term to the design. This new Term will connect by number. If any Term in the design connects by number, then all Terms in the design need to connect by number. |
| `keysight.ads.de.db_uu.Design.add_pin_fig_for_term_type` | function | `(self, term_type: keysight.ads.de._pde.db.TermType \| str, loc: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> 'PinFig'` |  |
| `keysight.ads.de.db_uu.Design.add_power_term` | function | `(self, term_name: str, power: str, default_net: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.Design.add_term` | function | `(self, net: 'Net', term_name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>) -> 'Term'` | Add a term to the design. This new Term will connect by name. If any Term in the design connects by name, then all Terms in the design need to connect by name. |
| `keysight.ads.de.db_uu.Design.config_view_name` | property | `` | The config view name for this design. Will be empty if there is no simulation setting for config view. |
| `keysight.ads.de.db_uu.Design.default_wire_layer` | property | `` | The default wire layer for wires. This is intended for schematics and typically returns LayerId(228). |
| `keysight.ads.de.db_uu.Design.find_term` | function | `(self, term_name: str) -> Optional[ForwardRef('Term')]` |  |
| `keysight.ads.de.db_uu.Design.find_term_numbered` | function | `(self, term_number: int) -> Optional[ForwardRef('Term')]` |  |
| `keysight.ads.de.db_uu.Design.get_preference` | function | `(self, preference: Union[ForwardRef('WorkspacePreference'), ForwardRef('LibSpecificPreference')]) -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.db_uu.Design.get_term_iter` | function | `(self) -> 'TermIter'` |  |
| `keysight.ads.de.db_uu.Design.is_schematic` | property | `` |  |
| `keysight.ads.de.db_uu.Design.set_preference` | function | `(self, preference: Union[ForwardRef('WorkspacePreference'), ForwardRef('LibSpecificPreference')], value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.db_uu.Design.terms` | property | `` |  |
| `keysight.ads.de.db_uu.DesignAttrType` | class | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.CELL_NAME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.CELL_TYPE` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.LAST_SAVED_TIME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.LIB_NAME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.VIEW_NAME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignMode` | class | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.DesignMode.APPEND` | DesignMode | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.DesignMode.READ_ONLY` | DesignMode | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.DesignMode.WRITE` | DesignMode | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.Donut.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Donut.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Donut.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Donut.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Dot.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Dot.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Dot.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Dot.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Ellipse.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Ellipse.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Ellipse.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Ellipse.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Boundary Walls for momentum simulation. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.box` | property | `` | A copy of the boundary wall's box. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_box` | function | `(design: keysight.ads.de.db_uu._design.Design, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create a box boundary wall. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_fem_symmetry` | function | `(design: keysight.ads.de.db_uu._design.Design, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create a FEM symmetry boundary wall. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_partial_waveguide` | function | `(design: keysight.ads.de.db_uu._design.Design, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create an incomplete waveguide boundary wall. This should not be used except when trying to recreate an incomplete waveguide. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_waveguide` | function | `(design: keysight.ads.de.db_uu._design.Design, horizontal: bool, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create a waveguide boundary wall. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_box` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_fem_symmetry` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_horizontal_waveguide` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_partial_waveguide` | property | `` | True if this is a waveguide that is incomplete. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_vertical_waveguide` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.move` | function | `(self, offset: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> None` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.props` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.EvalText` | class | `(design: keysight.ads.de.db_uu._design.Design, layer_id: keysight.ads.de.db._layer_id.LayerId, expression: str, evaluator: str, origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], font_name: str, height: float, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.CENTER_LEFT: 1>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>, has_overbar: bool = False, is_visible: bool = True, is_drafting: bool = True) -> None` | Custom text with an evaluator that determines what text gets displayed. |
| `keysight.ads.de.db_uu.EvalText.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.EvalText.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.EvalText.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.EvalText.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Fig.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Fig.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Fig.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.FigGroup` | class | `(design: 'Design', name: str) -> None` | A collection of figures that can be reused. This collection is called a Group in the ADS UI. A Pin is considered to be a member of a FigGroup if all of its PinFigs are members. A composite object is considered to be a... |
| `keysight.ads.de.db_uu.FigGroup.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.FigGroup.add_objects` | function | `(self, objects: collections.abc.Sequence[keysight.ads.de.db_uu._db_x.ApolloObject]) -> None` | Add the objects to this FigGroup if not already a member. |
| `keysight.ads.de.db_uu.FigGroup.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.FigGroup.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.FigGroup.members` | property | `` |  |
| `keysight.ads.de.db_uu.FigGroup.remove_from_fig_group` | function | `(self, obj: keysight.ads.de.db_uu._db_x.ApolloObject) -> None` | Remove obj from this FigGroup. If obj is a pin, all of its PinFigs will be removed. If obj is a composite object, all of its Figs will be removed. |
| `keysight.ads.de.db_uu.FigGroupMem` | class | `(fig_group: 'FigGroup', fig: 'Fig') -> None` | A link between a FigGroup and a member object (Fig). |
| `keysight.ads.de.db_uu.FigGroupMem.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.FigGroupMem.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.FigGroupMem.fig` | property | `` | The Fig represented by this member. |
| `keysight.ads.de.db_uu.FigGroupMem.fig_group` | property | `` | The FigGroup that contains this member. |
| `keysight.ads.de.db_uu.FigGroupMem.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.FigGroupMem.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.FigGroupMem.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.FigGroupMem.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.FigGroupMem.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.FigGroupMem.props` | property | `` |  |
| `keysight.ads.de.db_uu.FigGroupMem.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.Form.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.Group.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Group.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Group.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.Group.members` | property | `` |  |
| `keysight.ads.de.db_uu.GroupMember` | class | `(group: keysight.ads.de.db_uu._db_x.Group, obj: keysight.ads.de.db_uu._db_x.ApolloObject, is_leader: bool = False) -> None` | A link between a Group and a member object. |
| `keysight.ads.de.db_uu.GroupMember.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.GroupMember.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.GroupMember.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.GroupMember.group` | property | `` | The group that contains this member. |
| `keysight.ads.de.db_uu.GroupMember.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.GroupMember.is_leader` | property | `` | True if this member is the leader of the group. |
| `keysight.ads.de.db_uu.GroupMember.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.GroupMember.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.GroupMember.object` | property | `` | The object associated with this member. This may be None if the group contains objects that are not supported by ADS. |
| `keysight.ads.de.db_uu.GroupMember.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.GroupMember.props` | property | `` |  |
| `keysight.ads.de.db_uu.GroupMember.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.Instance.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Instance.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.Instance.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Instance.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.Instance.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.Instance.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Instance.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.Instance.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.Instance.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.Instance.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.Instance.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.Instance.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.Instance.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.Instance.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.Instance.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.Instance.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.Instance.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Instance.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.InstAttrDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstAttrDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.InstAttrDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.InstAttrType` | class | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.CELL_NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.IS_BOUND` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.LIB_NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.NUM_BITS` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.VIEW_NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstPin` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents the physical connection between an instance terminal and a pin on the master design. Note: There is no design object that represents an instance pin. This class is for convenience so you can find the snap p... |
| `keysight.ads.de.db_uu.InstPin.add_label` | function | `(self, label: str, pt: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None, font_name: str = '', height: float = 0, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.LOWER_LEFT: 2>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>) -> 'AttrDisplay'` | Add a net name label to this InstPin's InstTerm. This will also change the net of the InstTerm. |
| `keysight.ads.de.db_uu.InstPin.find_first_wire_label` | function | `(self) -> Optional[ForwardRef('AttrDisplay')]` | find_first_wire_label is deprecated, and will be removed in the 2027 release. Use net_label instead. |
| `keysight.ads.de.db_uu.InstPin.inst_pin_id` | property | `` | The identifier for this InstPin. The id is typically the inst_term_id with additional information if the term is unbound or the master pin is missing. |
| `keysight.ads.de.db_uu.InstPin.inst_term` | property | `` |  |
| `keysight.ads.de.db_uu.InstPropDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.InstPropDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstPropDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.InstPropDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.InstTerm` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a connection between a net and a terminal in the master of an instance. If either the instance or term is multibit, the number of bits in the net must match the number of bits in the instance times the numb... |
| `keysight.ads.de.db_uu.InstTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.InstTerm.add_label` | function | `(self, label: str, pt: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None, font_name: str = '', height: float = 0, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.LOWER_LEFT: 2>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>) -> 'AttrDisplay'` | Add a net name label to this InstTerm. This will also change the net of this InstTerm. |
| `keysight.ads.de.db_uu.InstTerm.bits` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstTerm.find_first_wire_label` | function | `(self) -> Optional[ForwardRef('AttrDisplay')]` | find_first_wire_label is deprecated, and will be removed in the 2027 release. Use net_label instead. |
| `keysight.ads.de.db_uu.InstTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.InstTerm.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.InstTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.InstTerm.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.inst_term_id` | property | `` | The unique identifier for this InstTerm. The id is of the form '<instance_name>.<term_id>' where <instance_name> is the name of the instance and <term_id> is either the term name or term number depending on how this I... |
| `keysight.ads.de.db_uu.InstTerm.instance` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.is_bound` | property | `` | Return True if this InstTerm is bound to the matching terminal on the master design. |
| `keysight.ads.de.db_uu.InstTerm.is_implicit` | property | `` | True if this InstTerm was implicitly created as part of a multi-bit InstTerm. |
| `keysight.ads.de.db_uu.InstTerm.is_numbered` | property | `` | Return True if this InstTerm binds to the terminal by number. |
| `keysight.ads.de.db_uu.InstTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.InstTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.InstTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.net_label` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.InstTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.term` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.term_name` | property | `` | Return the term name if this InstTerm uses binds the term by name. Otherwise, raise an exception. |
| `keysight.ads.de.db_uu.InstTerm.term_number` | property | `` | Return the term number if this InstTerm binds the term by number. Otherwise, raise an exception. |
| `keysight.ads.de.db_uu.InstTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.InstTermAttrType` | class | `` | Members: NAME |
| `keysight.ads.de.db_uu.InstTermAttrType.NAME` | InstTermAttrType | `` | Members: NAME |
| `keysight.ads.de.db_uu.InstTermAttrType.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.InstTermAttrType.value` | property | `` |  |
| `keysight.ads.de.db_uu.InstTermIter` | class | `(obj: 'Instance \| Net')` | An iterator for InstTerms in a Design. |
| `keysight.ads.de.db_uu.Interconnect` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | An Interconnect is a composite object used to implement a Trace. |
| `keysight.ads.de.db_uu.Interconnect.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Interconnect.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Interconnect.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Interconnect. |
| `keysight.ads.de.db_uu.Interconnect.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.Interconnect.members` | property | `` |  |
| `keysight.ads.de.db_uu.Keepout.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Keepout.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.LCVName.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.LimitRegionOption` | class | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MAY_TOUCH_ONLY_BOUNDING_BOX` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MUST_CONTAIN_OBJECT` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MUST_TOUCH_ACTUAL_OBJECT` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MUST_TOUCH_OBJECT_EDGE` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.Line.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Line.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Line.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Line.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Line. |
| `keysight.ads.de.db_uu.Line.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.LineThickness` | class | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineThickness.MEDIUM` | LineThickness | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineThickness.THICK` | LineThickness | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineThickness.THIN` | LineThickness | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineTypeInfo.layer_id` | property | `` | The LayerId used by this LineTypeInfo. If line_item is set, the layer_id is ignored. Setting the layer_id will clear the LineItem. |
| `keysight.ads.de.db_uu.LineTypeInfo.line_item` | property | `` | The LineItem (from the technology) used by this LineTypeInfo. If line_item is not None, the layer_id is ignored. Setting the layer_id will clear the LineItem. |
| `keysight.ads.de.db_uu.LineTypeInfo.teardrop_definition_back` | property | `` | Returns a copy of the back teardrop definition. teardrop_definition_back is deprecated, and will be removed in the 2027 release. Use teardrop_back |
| `keysight.ads.de.db_uu.LineTypeInfo.teardrop_definition_front` | property | `` | Returns a copy of the front teardrop definition. teardrop_definition_front is deprecated, and will be removed in the 2027 release. Use teardrop_front |
| `keysight.ads.de.db_uu.MirrorType` | class | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.MirrorType.MIRROR_X` | MirrorType | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.MirrorType.MIRROR_Y` | MirrorType | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.MirrorType.NONE` | MirrorType | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.ModelCb` | class | `(callback_type: keysight.ads.de._pde.ModelCbType, callback: collections.abc.Callable) -> None` | A model callback that is implemented in Python. |
| `keysight.ads.de.db_uu.ModelCb.item_modified_callback` | function | `(callback: collections.abc.Callable[['Instance'], None]) -> 'ModelCb'` |  |
| `keysight.ads.de.db_uu.ModelCb.item_netlist_callback` | function | `(callback: collections.abc.Callable[['StandardInstance'], str]) -> 'ModelCb'` |  |
| `keysight.ads.de.db_uu.ModelCbAEL` | class | `(callback_type: keysight.ads.de._pde.ModelCbType, vocabulary: str, function: str, client_data: object, enabled: bool = True) -> None` | A model callback that is implemented in AEL. |
| `keysight.ads.de.db_uu.ModelCbBase` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for callbacks used by model definitions and model parameters. See :class:`de.db.ModelParam` and :class:`de.db.ModelDef`. Each callback function can be implemented in Python or AEL. |
| `keysight.ads.de.db_uu.ModelCbType` | class | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.ITEM_MODIFIED` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.ITEM_NETLIST` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.PARAMETER_DEFAULT_VALUE` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.PARAMETER_MODIFIED` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelDef` | class | `(name: str, label: str) -> None` | A model definition implemented in Python. |
| `keysight.ads.de.db_uu.ModelDef.is_bom_item` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDef.is_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDef.legacy_dialog_name` | property | `` | The name used by some components to determine which Parameter dialog to use for editing. |
| `keysight.ads.de.db_uu.ModelDefAEL` | class | `()` | A model definition implemented in AEL. |
| `keysight.ads.de.db_uu.ModelDefAEL.can_auto_increment` | property | `` | True if the first parameter of this model can be auto-incremented. |
| `keysight.ads.de.db_uu.ModelDefAEL.is_bom_item` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefAEL.is_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefAEL.legacy_dialog_name` | property | `` | The name used by some components to determine which Parameter dialog to use for editing. |
| `keysight.ads.de.db_uu.ModelDefBase` | class | `()` | A model definition, sometimes referred to as an item definition or component definition, contains the parameter definitions for a particular component or design. |
| `keysight.ads.de.db_uu.ModelDefBase.is_bom_item` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefBase.is_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefBase.legacy_dialog_name` | property | `` | The name used by some components to determine which Parameter dialog to use for editing. |
| `keysight.ads.de.db_uu.ModelParamType` | class | `(*values)` | Create a collection of name/value pairs. Example enumeration: >>> class Color(Enum): ... RED = 1 ... BLUE = 2 ... GREEN = 3 Access them by: - attribute access: >>> Color.RED <Color.RED: 1> - value lookup: >>> Color(1)... |
| `keysight.ads.de.db_uu.ModelUnitType` | class | `(*values)` | Create a collection of name/value pairs. Example enumeration: >>> class Color(Enum): ... RED = 1 ... BLUE = 2 ... GREEN = 3 Access them by: - attribute access: >>> Color.RED <Color.RED: 1> - value lookup: >>> Color(1)... |
| `keysight.ads.de.db_uu.ModelUnitType.TEMPERATURE` | ModelUnitType | `` |  |
| `keysight.ads.de.db_uu.MomentumMesh.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.MomentumMesh.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Net` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for net objects. Nets represent logical connections between elements in a design. |
| `keysight.ads.de.db_uu.Net.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Net.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Net.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Net.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Net.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.NetAttrType` | class | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.IS_EMPTY` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.IS_GLOBAL` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.IS_IMPLICIT` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.NAME` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.NUM_BITS` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.SIG_TYPE` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetlistNode.is_grounded` | property | `` |  |
| `keysight.ads.de.db_uu.NullForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.OAParamType` | class | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.APP_PARAM` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.BOOLEAN` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.DOUBLE` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.FLOAT` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.INT` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.STRING` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.TIME` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.open_design` | function | `(name: 'CellviewRefLike', mode: keysight.ads.de._pde.db.DesignMode \| str = <DesignMode.READ_ONLY: 0>) -> keysight.ads.de.db_uu._design.Design` | Open a design from an open library in the active workspace. Parameters ---------- name: CellviewRefLike The name of the design, usually of the form "LibraryName:CellName:schematic" mode: DesignMode \| str Specifies the... |
| `keysight.ads.de.db_uu.Orientation` | class | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MX` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MXR90` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MY` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MYR90` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R0` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R180` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R270` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R90` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Param.evaluate_no_expr` | function | `(self) -> str` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.Param.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.Param.item` | property | `` |  |
| `keysight.ads.de.db_uu.Param.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamBase` | class | `()` | Base class that holds both a parameter item and its definition. See :class:`ParamItem` and :class:`de.db.ModelParam`. |
| `keysight.ads.de.db_uu.ParamBase.evaluate_no_expr` | function | `(self) -> Union[str, list[str], list[list[str]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.ParamBase.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str, list[Union[bool, int, float, str]], list[list[Union[bool, int, float, str]]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamBase.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamBase.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamCompound.display_value` | property | `` | Returns a list of copies of the sub parameter display values. Do not attempt to assign values to individual elements of that list. Use sub_params if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamCompound.evaluate_no_expr` | function | `(self) -> list[str]` | Prepare this compound parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamCompound.evaluate_without_expr` | function | `(self) -> list[typing.Union[bool, int, float, str]]` | Prepare this compound parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamCompound.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamCompound.netlist_value` | property | `` | Returns a list of copies of the sub parameter netlist values. Do not attempt to assign values to individual elements of that list. Use sub_params if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamCompound.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamCompound.value` | property | `` | Returns a list of copies of the sub parameter values. Do not attempt to assign values to individual elements of that list. Use sub_params if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamItem` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for parameter items. See also :class:`de.db.ModelParam` which is the parameter definition. The classes derived from ParamItem are used for default values in ModelParam and to hold instance and terminal para... |
| `keysight.ads.de.db_uu.ParamItem.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItem.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItem.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItem.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItem.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemCompound` | class | `(param_name: str, form_name: str, subparams: collections.abc.Sequence[keysight.ads.de.db._parameters.ParamItem]) -> None` | A parameter item that consists one or more sub-parameters. The number of sub-parameters must match the number of sub-parameters on the compound form that is used to create the parameter definition. The sub-parameters ... |
| `keysight.ads.de.db_uu.ParamItemCompound.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemCompound.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemCompound.sub_params` | property | `` | The sub-parameters (or fields) that define this compound parameter. |
| `keysight.ads.de.db_uu.ParamItemConst` | class | `(param_name: str, form: Union[str, keysight.ads.de.db._forms.Form, NoneType] = None) -> None` | A parameter item whose value is determined by its form - (see :class:`de.db.ConstForm`). |
| `keysight.ads.de.db_uu.ParamItemConst.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemConst.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemConst.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemNull` | class | `(param_name: str) -> None` | A parameter item with no value. |
| `keysight.ads.de.db_uu.ParamItemNull.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemNull.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemNull.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemNull.value` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated` | class | `(param_name: str, repeats: collections.abc.Sequence[keysight.ads.de.db._parameters.ParamItem]) -> None` | A parameter item that holds a list of one or more repeats. The parameter definition's formset dictates the forms that can be used for each repeat. A repeat cannot also be repeated but may use compound forms, having th... |
| `keysight.ads.de.db_uu.ParamItemRepeated.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemRepeated.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemRepeated.repeats` | property | `` | The repeats of this repeatable parameter. |
| `keysight.ads.de.db_uu.ParamItemString` | class | `(param_name: str, form: Union[str, keysight.ads.de.db._forms.Form, NoneType] = None, param_value: Optional[str] = None) -> None` | A string-valued parameter item. |
| `keysight.ads.de.db_uu.ParamItemString.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemString.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemString.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemString.value` | property | `` | The value of this ParamItem. When assigning values, prefer to use Param.value. |
| `keysight.ads.de.db_uu.ParamIter` | class | `(owner: 'InstanceDbu \| InstanceUu \| TermBaseDbu \| TermBaseUu') -> None` | An iterator that can be used to visit parameters of an instance or terminal. |
| `keysight.ads.de.db_uu.ParamIter.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamNonRepeated.evaluate_no_expr` | function | `(self) -> Union[str, list[str]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.ParamNonRepeated.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str, list[Union[bool, int, float, str]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamNonRepeated.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamNonRepeated.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamRepeated.append_repeat` | function | `(self, value: Union[str, collections.abc.Sequence[str]]) -> None` | Clone the last repeat and set its value. append_repeat is deprecated, and will be removed in the 2027 release. Use: repeat = repeats.clone(value); repeat.value = value. |
| `keysight.ads.de.db_uu.ParamRepeated.display_value` | property | `` | Returns a list of copies of the repeat display values. Do not attempt to assign values to individual elements of that list. Use repeats if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamRepeated.evaluate_no_expr` | function | `(self) -> Union[list[str], list[list[str]]]` | Prepare this repeated parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamRepeated.evaluate_without_expr` | function | `(self) -> list[typing.Union[bool, int, float, str, list[typing.Union[bool, int, float, str]]]]` | Prepare this repeated parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamRepeated.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamRepeated.netlist_value` | property | `` | Returns a list of copies of the repeat netlist values. Do not attempt to assign values to individual elements of that list. Use repeats if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamRepeated.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamRepeated.value` | property | `` | Returns a list of copies of the repeat values. Do not attempt to assign values to individual elements of that list. Use repeats if you need to modify individual values. |
| `keysight.ads.de.db_uu.Path.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Path.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Path.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Path.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Path. |
| `keysight.ads.de.db_uu.Path.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PathSeg.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PathSeg.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PathSeg.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PathSeg.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PathStyle` | class | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.EXTEND` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.ROUND` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.TRUNCATE` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.VARIABLE` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PCBBase.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PCBBase.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.PCBBase.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBBase.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBBase.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBBase.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBBase.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBBase.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBBase.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.PCBBase.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.PCBBase.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBBase.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.PCBBase.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.PCBBase.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.PCBBase.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.PCBBase.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.PCBBase.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PCBBase.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PCBBase.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.PCBPad.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PCBPad.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.PCBPad.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBPad.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBPad.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBPad.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBPad.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBPad.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBPad.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.PCBPad.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.PCBPad.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBPad.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.PCBPad.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.PCBPad.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.PCBPad.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.PCBPad.padstack_name` | property | `` | Name of the padstack template that defines this pad. The name will be in the form lib_name:padstack_name. |
| `keysight.ads.de.db_uu.PCBPad.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.PCBPad.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PCBPad.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PCBPad.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.PCBVia` | class | `(design: 'Design', master: 'CellviewRefLike \| Design', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, name: Optional[str] = None, angle: Optional[float] = None, mirror: Union[keysight.ads.de._pde.db.MirrorType, str, NoneType] = None) -> None` | Represents a PCB Via instance in layout. The Via can be specified by rule or with a Padstack template definition and specified layers. Vias with Padstack definitions can have a specified drill layer, specified top and... |
| `keysight.ads.de.db_uu.PCBVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PCBVia.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.PCBVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBVia.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBVia.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBVia.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBVia.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBVia.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.PCBVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.PCBVia.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBVia.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.PCBVia.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.PCBVia.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.PCBVia.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.PCBVia.padstack_name` | property | `` | Name of the padstack template that defines this via. The name will be in the form lib_name:padstack_name. This will be empty if the via was defined by a rule. |
| `keysight.ads.de.db_uu.PCBVia.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.PCBVia.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PCBVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PCBVia.rule_name` | property | `` | Name of the via rule that defines this via. The name will be in the form lib_name:rule_name. This will be empty if the via was not defined by a rule. |
| `keysight.ads.de.db_uu.PCBVia.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.PCellInfo.reference_name` | property | `` | The reference name for reference PCells. |
| `keysight.ads.de.db_uu.PCellInfo.supports_psn_behavior` | property | `` | True if the PCell supports PSN behavior. |
| `keysight.ads.de.db_uu.PCellInfo.supports_scaling` | property | `` | True if the PCell supports scaling. |
| `keysight.ads.de.db_uu.PCellType` | class | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.AEL_MACRO` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.GENERIC` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.LAYER_MAPPING` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.LISP_MACRO` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.MISSING` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.NONE` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.PSN` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.PYCELL` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.PYTHON_MACRO` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.REFERENCE` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.SMART_MOUNT` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.UNKNOWN` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.VIA_PAD` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.Pin` | class | `(term: keysight.ads.de.db_uu._db_x.Term, pin_figs: Union[keysight.ads.de.db_uu._db_x.PinFig, list[keysight.ads.de.db_uu._db_x.PinFig]], *, angle: Optional[float] = None, add_annot: Optional[bool] = None) -> None` | Represents the physical connection between a terminal and a net. A pin can have zero or more PinFigs. Use PinFigIter(pin) to iterate over the pins. |
| `keysight.ads.de.db_uu.Pin.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Pin.add_label` | function | `(self, label: str, pt: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None, font_name: str = '', height: float = 0, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.LOWER_LEFT: 2>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>) -> 'AttrDisplay'` | Add a net name label to this Pin. This will also change the net of the pin's term. |
| `keysight.ads.de.db_uu.Pin.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Pin.find_first_wire_label` | function | `(self) -> Optional[keysight.ads.de.db_uu._db_x.AttrDisplay]` | find_first_wire_label is deprecated, and will be removed in the 2027 release. Use net_label instead. |
| `keysight.ads.de.db_uu.Pin.has_ads_term_annotation` | property | `` | Return True if this Pin has ADS Name, Number or parameter annotation. |
| `keysight.ads.de.db_uu.Pin.placement_status` | property | `` | PlacementStatus for this pin (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.Pin.term` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.term_name` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.term_number` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.update_pin_annotation` | function | `(self, annot_data: Optional[ForwardRef('PinAnnotData')] = None, *, preserve_origin: bool = True) -> None` | Update the pin annotation. If annot_data is None, the design preferences will be used. If preserve_origin is True, the annotation origin will not be moved. |
| `keysight.ads.de.db_uu.PinAnnotData.term_name_layer` | property | `` | The layer used for term name annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.term_number_layer` | property | `` | The layer used for term number annotation. |
| `keysight.ads.de.db_uu.PinFig.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PinFig.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PinFig.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PinFig.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PlacementStatus` | class | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.FIXED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.LOCKED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.PlacementStatus.NONE` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.PLACED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.str` | property | `` | Return the string representation of the PlacementStatus. |
| `keysight.ads.de.db_uu.PlacementStatus.UNPLACED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.value` | property | `` |  |
| `keysight.ads.de.db_uu.Plane` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | A plane is a large shape (composite) on a single net. The layer is usually a conductor (e.g. copper). The net is often ground or power. |
| `keysight.ads.de.db_uu.Plane.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Plane.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Plane.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.Plane.members` | property | `` |  |
| `keysight.ads.de.db_uu.Plane.placement_status` | property | `` | PlacementStatus for this plane (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PlaneInfo.min_island_area` | property | `` | Specifies the minimum area of an island that gets preserved when removing islands by area. |
| `keysight.ads.de.db_uu.PlaneInfo.remove_islands_mode` | property | `` | Determines how unconnected islands within the Plane's outline get removed. |
| `keysight.ads.de.db_uu.PlaneInfo.RemoveIslandsMode` | class | `` | Describes island removal. Members: REMOVE_NONE : 'RemoveNone': Does not remove any islands. REMOVE_ALL : 'RemoveAll: Removes all islands. REMOVE_BY_AREA : 'RemoveByArea': Removes islands whose area is less than the mi... |
| `keysight.ads.de.db_uu.PlaneInfo.same_props` | function | `(self, other: 'PlaneInfo') -> bool` | Determine if the essential properties are the same. This is not the same as equality because properties that are not enabled are ignored. |
| `keysight.ads.de.db_uu.PlaneInfo.smoothing_enabled` | property | `` | If True, the Plane's outline gets smoothed, possibly removing small features and rounding corners. |
| `keysight.ads.de.db_uu.PlaneInfo.use_round_corners_when_smoothing` | property | `` | If True, round corners created when features are removed by smoothing. Otherwise bevel the corners. |
| `keysight.ads.de.db_uu.Polygon.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Polygon.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Polygon.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Polygon.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Polygon. |
| `keysight.ads.de.db_uu.Polygon.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Polyline.empty` | property | `` |  |
| `keysight.ads.de.db_uu.PropDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PropDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PropDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PropDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PropType` | class | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.APP` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.BOOLEAN` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.DOUBLE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.DOUBLE_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.ENUM` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.FLOAT` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.FLOAT_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.HIER` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.INT` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.INT_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.STRING` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.TIME` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.TIME_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.Rect.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Rect.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Rect.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Rect.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Ref.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Ref.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Ref.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Ref.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.Ref.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.RefIter` | class | `(design: 'Design') -> None` | An iterator for Refs (Instance or Via references) in a Design. |
| `keysight.ads.de.db_uu.RepeatedForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.ScalarInst.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ScalarInst.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.ScalarInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.ScalarInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.ScalarInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ScalarInst.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.ScalarInst.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.ScalarInst.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.ScalarInst.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.ScalarInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.ScalarInst.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.ScalarInst.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.ScalarInst.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarInst.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.ScalarInst.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.ScalarInst.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ScalarInst.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.ScalarNet.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ScalarNet.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.ScalarNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarNet.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.ScalarNet.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm` | class | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A scalar term without bus-name syntax. |
| `keysight.ads.de.db_uu.ScalarTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ScalarTerm.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.ScalarTerm.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.ScalarTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.ScalarTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.ScalarTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.ScalarTerm.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.ScalarTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.ScalarTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.ScalarTerm.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.ScalarTerm.name` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.ScalarTerm.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.ScalarTerm.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.ScalarTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.ScalarTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.ScalarTerm.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.SecondaryTermInfo` | class | `(term_name: str, is_positive: bool)` | Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo.is_positive` | property | `` | True if this term is a positive term. This is used to determine the polarity of the term in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo.term_name` | property | `` | The name of the secondary term. |
| `keysight.ads.de.db_uu.Shape.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Shape.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Shape.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Shape.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIterNetOption` | class | `` | Members: NET_SHAPES_ONLY PIN_AND_NET_SHAPES |
| `keysight.ads.de.db_uu.ShapeIterNetOption.NET_SHAPES_ONLY` | ShapeIterNetOption | `` | Members: NET_SHAPES_ONLY PIN_AND_NET_SHAPES |
| `keysight.ads.de.db_uu.ShapeIterNetOption.PIN_AND_NET_SHAPES` | ShapeIterNetOption | `` | Members: NET_SHAPES_ONLY PIN_AND_NET_SHAPES |
| `keysight.ads.de.db_uu.ShapeOption` | class | `` | Members: ALL_SHAPES |
| `keysight.ads.de.db_uu.ShapeOption.ALL_SHAPES` | ShapeOption | `` | Members: ALL_SHAPES |
| `keysight.ads.de.db_uu.SignalType` | class | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.ANALOG` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.CLOCK` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.GROUND` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.POWER` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.RESET` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.SCAN` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.SIGNAL` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.TIE_HI` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.TIE_LO` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.TIE_OFF` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.StackedPCBVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.StackedPCBVia.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.StackedPCBVia.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.StackedPCBVia.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.StackedPCBVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.StackedPCBVia.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.StackedPCBVia.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.StackedPCBVia.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.StackedPCBVia.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.StackedPCBVia.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.StackedPCBVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.rule_name` | property | `` | Name of the via rule that defines this via. The name will be in the form lib_name:rule_name. This will be empty if the via was not defined by a rule. |
| `keysight.ads.de.db_uu.StackedPCBVia.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.std_string_param` | function | `(value: str) -> keysight.ads.de.db._parameters.ParamItemString` | Make a ParamItemString using the StdForm. |
| `keysight.ads.de.db_uu.StdVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.StdVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.StdVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.StdVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.StdVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.StringForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.StringFormWithAELCallbacks.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.StringFormWithCallbacks.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle` | class | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.NONE` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.TEARDROP_ANGLE` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.WIDTH_AND_HEIGHT` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.WIDTH_TANGENT` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropValueUnits` | class | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.TeardropValueUnits.DB_UNITS` | TeardropValueUnits | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.TeardropValueUnits.RATIO` | TeardropValueUnits | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.TeardropValueUnits.VALUE` | TeardropValueUnits | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.Term` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Terminals represent a logical connection points for a design. The pins associated with terminals represent the physical connection points. The nets associated with terminals through the terminals to the parent design.... |
| `keysight.ads.de.db_uu.Term.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Term.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.Term.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.Term.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Term.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.Term.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.Term.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.Term.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.Term.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Term.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.Term.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.Term.name` | property | `` |  |
| `keysight.ads.de.db_uu.Term.net` | property | `` |  |
| `keysight.ads.de.db_uu.Term.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.Term.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.Term.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.Term.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.Term.props` | property | `` |  |
| `keysight.ads.de.db_uu.Term.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.Term.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.Term.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.Term.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.Term.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.Term.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.TermAttrType` | class | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.HAS_PINS` | TermAttrType | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.NAME` | TermAttrType | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.TermAttrType.NUM_BITS` | TermAttrType | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.str` | property | `` | Return the string representation of the TermAttrType. |
| `keysight.ads.de.db_uu.TermAttrType.value` | property | `` |  |
| `keysight.ads.de.db_uu.TermIter` | class | `(obj: 'Design \| Net') -> None` | An iterator for Terms in a Design. |
| `keysight.ads.de.db_uu.TermType` | class | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.INPUT` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.INPUT_OUTPUT` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.JUMPER` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.TermType.OUTPUT` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.str` | property | `` | Return the string representation of the TermType. |
| `keysight.ads.de.db_uu.TermType.SWITCH` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.TRISTATE` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.UNUSED` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.value` | property | `` |  |
| `keysight.ads.de.db_uu.Text.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Text.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Text.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Text.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.TextAlignment` | class | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.CENTER_CENTER` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.CENTER_LEFT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.CENTER_RIGHT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.LOWER_CENTER` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.LOWER_LEFT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.LOWER_RIGHT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.UPPER_CENTER` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.UPPER_LEFT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.UPPER_RIGHT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextBase.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.TextBase.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextBase.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextBase.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.TextDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.TextDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.TextDisplayFormat` | class | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextDisplayFormat.NAME` | TextDisplayFormat | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextDisplayFormat.NAME_VALUE` | TextDisplayFormat | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextDisplayFormat.VALUE` | TextDisplayFormat | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextOverride` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | A text object that supports overriding text from an instance master. |
| `keysight.ads.de.db_uu.TextOverride.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.TextOverride.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextOverride.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextOverride.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Transaction` | class | `(design: 'Design \| DesignDb', command: str = 'Edit') -> None` | Operations performed between when the Transaction is created and when it is committed may be undone. This provides the ability to group multiple operations together and undo them with a call to rollback. |
| `keysight.ads.de.db_uu.Transaction.is_empty` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.TransactionState` | class | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.TransactionState.COMMITTED` | TransactionState | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.TransactionState.IN_PROGRESS` | TransactionState | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.TransactionState.ROLLED_BACK` | TransactionState | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.VectorInst.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.VectorInst.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.VectorInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.VectorInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.VectorInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.VectorInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInst.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInst.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInst.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.VectorInst.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.VectorInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.VectorInst.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.VectorInst.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.VectorInst.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInst.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.VectorInst.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.VectorInst.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.VectorInst.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.VectorInstBit.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.VectorInstBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.VectorInstBit.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.VectorInstBit.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.VectorInstBit.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInstBit.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInstBit.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInstBit.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.VectorInstBit.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.VectorInstBit.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.VectorInstBit.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.VectorInstBit.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.VectorInstBit.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInstBit.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.VectorInstBit.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.Via.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Via.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Via.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Via.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.Via.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement` | class | `(names: collections.abc.Sequence[str] = []) -> None` | ViaElement identifies the Via inside an Interconnect. |
| `keysight.ads.de.db_uu.ViaElement.add_via_name` | function | `(self, name: str) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement.add_via_names` | function | `(self, names: collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement.clear_vias` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.ViaElement.via_names` | property | `` |  |
| `keysight.ads.de.db_uu.ViaIterNetOptions` | class | `` | Members: NET_VIAS_ONLY PIN_AND_NET_VIAS |
| `keysight.ads.de.db_uu.ViaIterNetOptions.NET_VIAS_ONLY` | ViaIterNetOptions | `` | Members: NET_VIAS_ONLY PIN_AND_NET_VIAS |
| `keysight.ads.de.db_uu.ViaIterNetOptions.PIN_AND_NET_VIAS` | ViaIterNetOptions | `` | Members: NET_VIAS_ONLY PIN_AND_NET_VIAS |
| `keysight.ads.de.db_uu.WhichConnection` | class | `` | Members: BEGIN END |
| `keysight.ads.de.db_uu.WhichConnection.BEGIN` | WhichConnection | `` | Members: BEGIN END |
| `keysight.ads.de.db_uu.WhichConnection.END` | WhichConnection | `` | Members: BEGIN END |

### `keysight.ads.emtools`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.emtools.create_empro_view` | function | `(empro_lcv: tuple[str, str, str], tool: str, layout_lcv: tuple[str, str, str], substrate_ls: tuple[str, str]) -> None` | Create a view, saved on disk, that can be opened in the specified EM tool. Parameters ---------- empro_lcv Tuple containing the library name, cell name and the EM view name to be created. tool EM tool name, eihter 'pi... |
| `keysight.ads.emtools.create_empro_view_ex` | function | `(empro_lib: str, empro_cell: str, empro_view: str, tool: str, layout_lib: str, layout_cell: str, layout_view: str, substrate_lib: str, substrate: str) -> None` |  |
| `keysight.ads.emtools.create_emproview` | function | `(empro_lcv: tuple, tool: str, layout_lcv: tuple, substrate_ls: tuple) -> None` | create_emproview is deprecated, and will be removed in the 2026 Update 1 release. Use create_empro_view instead. |
| `keysight.ads.emtools.create_emproview_ex` | function | `(empro_lib: str, empro_cell: str, empro_view: str, tool: str, layout_lib: str, layout_cell: str, layout_view: str, substrate_lib: str, substrate: str) -> None` | create_emproview_ex is deprecated, and will be removed in the 2026 Update 1 release. Use create_empro_view_ex instead. |
| `keysight.ads.emtools.deprecated` | function | `(version: str, message: Optional[str] = None)` | Mark a function or class as deprecated. :param version: release version in which the feature will be *removed*. :param message: additional deprecation message. |
| `keysight.ads.emtools.DesignRef` | class | `` |  |
| `keysight.ads.emtools.DesignRef.layout` | property | `` |  |
| `keysight.ads.emtools.DesignRef.layout_switch_list` | property | `` |  |
| `keysight.ads.emtools.DesignRef.set_layout` | instancemethod | `` | set_layout(self: keysight.ads.emtools._emtools.DesignRef, arg0: str, arg1: str, arg2: str) -> None |
| `keysight.ads.emtools.DesignRef.set_substrate` | instancemethod | `` | set_substrate(self: keysight.ads.emtools._emtools.DesignRef, arg0: str, arg1: str) -> None |
| `keysight.ads.emtools.DesignRef.substrate` | property | `` |  |
| `keysight.ads.emtools.Dict` | _SpecialGenericAlias | `(*args, **kwargs)` | A generic version of dict. |
| `keysight.ads.emtools.EmproSetup` | class | `(filepath__or__empro_lcv_tuple: str \| tuple \| None = None) -> 'EmproSetup'` | Class to work on the EM view setup. |
| `keysight.ads.emtools.EmproSetup.default_filename` | function | `(self) -> str` | Returns the default EM view setup file name. |
| `keysight.ads.emtools.EmproSetup.design_refs` | property | `` | The design references -- layout and substrate -- of the EM view setup. :getter: Returns this setup's design references. :setter: Sets this setup's design references. |
| `keysight.ads.emtools.EmproSetup.tool` | property | `` | The tool for this EM view setup. :getter: Returns this setup's tool. :setter: Sets this setup's tool. |
| `keysight.ads.emtools.EmproSetup.write` | function | `(self, filepath_or_lcv: str \| tuple) -> None` | Writes the EM view setup data. Parameters ---------- filepath_or_lcv Either provide a tuple of strings -- library name, cell name and view name -- or provide the view's setup filepath. |
| `keysight.ads.emtools.find_emsetup_view_name` | function | `(layout_lcv: tuple[str, str, str]) -> str` | Find the active EM Setup view name from the Layout view. Parameters ---------- layout_lcv Tuple containing the library name, cell name and the layout view name. Returns ------- The EM Setup view name Raises ------ Run... |
| `keysight.ads.emtools.get_substrate_info` | function | `(emsetup_lcv: tuple[str, str, str]) -> tuple[str, str]` | Get the substrate info of the EM Setup view. Parameters ---------- emsetup_lcv Tuple containing the library name, cell name and the EM Setup view name. Returns ------- Tuple containing the substrate library name and t... |
| `keysight.ads.emtools.update_empro_view` | function | `(empro_lcv: tuple[str, str, str]) -> None` | Update the EM view after a layout or substrate change. Updates the auxiliary files associated with the EM view: .adsPcells cache, adsMultiTechData.json, proj.ltd,... Parameters ---------- empro_lcv Tuple containing th... |
| `keysight.ads.emtools.version` | function | `() -> str` | Returns the version of the emtools package. |
| `keysight.ads.emtools.version_number` | function | `() -> int` |  |

### `keysight.edatoolbox.xxpro`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.xxpro.get_python_xxpro_location` | function | `(from_ads=True) -> str` | Returns the location of the python installed with xxPro. Parameters ---------- from_ads : bool, default=True If True get xxPro from ADS install folder, otherwise look for EMPROHOME environment variable. |
| `keysight.edatoolbox.xxpro.get_xxpro_location` | function | `(from_ads=True) -> str` | Returns the location of the latest installed xxPro. Parameters ---------- from_ads : bool, default=True If True get xxPro from ADS install folder, otherwise look for EMPROHOME environment variable. |
| `keysight.edatoolbox.xxpro.load_pro_view` | function | `(xxpro_lcv: keysight.edatoolbox.ads.LibraryCellView)` | Load an xxpro LibraryCellView into the empro.activeProject. Parameters ---------- xxpro_lcv : LibraryCellView An xxpro LibraryCellView object. Raises ------ ImportError Failed to import empro module. |
| `keysight.edatoolbox.xxpro.os` | module | `` | OS routines for NT or Posix depending on what system we're on. This exports: - all functions from posix or nt, e.g. unlink, stat, etc. - os.path is either posixpath or ntpath - os.name is either 'posix' or 'nt' - os.c... |
| `keysight.edatoolbox.xxpro.re` | module | `` | Support for regular expressions (RE). This module provides regular expression matching operations similar to those found in Perl. It supports both 8-bit and Unicode strings; both the pattern and the strings being proc... |
