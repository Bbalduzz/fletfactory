import math
from typing import List, Optional, Dict
from flet import Container, Row, Column, Control, alignment, MainAxisAlignment, CrossAxisAlignment, app

class WaterfallDelegate:
    def __init__(
        self,
        cross_axis_count: Optional[int] = None,
        max_cross_axis_extent: Optional[float] = None,
        main_axis_spacing: float = 0.0,
        cross_axis_spacing: float = 0.0,
    ):
        assert (cross_axis_count is not None) ^ (
            max_cross_axis_extent is not None
        ), "Must provide either cross_axis_count or max_cross_axis_extent"
        self.cross_axis_count = cross_axis_count
        self.max_cross_axis_extent = max_cross_axis_extent
        self.main_axis_spacing = main_axis_spacing
        self.cross_axis_spacing = cross_axis_spacing

    def get_cross_axis_count(self, width: float) -> int:
        if self.cross_axis_count is not None:
            return self.cross_axis_count
        return math.floor(
            width / (self.max_cross_axis_extent + self.cross_axis_spacing)
        )

    def get_child_cross_axis_extent(self, width: float) -> float:
        cross_axis_count = self.get_cross_axis_count(width)
        usable_width = max(
            0.0, width - self.cross_axis_spacing * (cross_axis_count - 1)
        )
        return usable_width / cross_axis_count


class WaterfallView(Column):
    def __init__(
        self,
        controls: Optional[List[Control]] = None,
        cross_axis_count: Optional[int] = None,
        max_cross_axis_extent: Optional[float] = None,
        main_axis_spacing: float = 0.0,
        cross_axis_spacing: float = 0.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.delegate = WaterfallDelegate(
            cross_axis_count=cross_axis_count,
            max_cross_axis_extent=max_cross_axis_extent,
            main_axis_spacing=main_axis_spacing,
            cross_axis_spacing=cross_axis_spacing,
        )
        self._controls = controls or []
        self.spacing = main_axis_spacing
        self._columns: List[Column] = []
        
    def _build_columns(self, width: float):
        cross_axis_count = self.delegate.get_cross_axis_count(width)
        child_width = self.delegate.get_child_cross_axis_extent(width)
        
        # Clear existing columns
        self._columns = []
        self.controls = []
        
        # Create columns
        for i in range(cross_axis_count):
            col = Column(
                spacing=self.delegate.main_axis_spacing,
                width=child_width,
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.CENTER,
            )
            self._columns.append(col)
        
        # Add columns to a row
        row = Row(
            controls=self._columns,
            spacing=self.delegate.cross_axis_spacing,
            alignment=MainAxisAlignment.START,
            vertical_alignment=CrossAxisAlignment.START,
        )
        self.controls.append(row)
        
        # Distribute items to columns
        column_heights = [0] * cross_axis_count
        for control in self._controls:
            # Find shortest column
            shortest_col_index = column_heights.index(min(column_heights))
            self._columns[shortest_col_index].controls.append(control)
            
            # Update column height (assuming control has height property)
            control_height = getattr(control, '_height', 500) # this works even without settings a real height cause the Containers are not expanded and we are sitting a huged default height
            column_heights[shortest_col_index] += control_height + self.delegate.main_axis_spacing
    
    def build(self):
        # This would be called when the control is added to the page
        # We need to know the width to calculate columns
        # In Flet, we might need to handle this differently
        # For now, assume width is set or we use a default
        width = getattr(self, 'width', 400)  # default width
        self._build_columns(width)
        return self