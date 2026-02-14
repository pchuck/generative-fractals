use std::collections::HashMap;

use crate::fractal::FractalType;
use crate::palette::PaletteType;
use crate::viewport::Viewport;

/// State that can be modified by commands
#[derive(Debug, Clone)]
pub struct AppState {
    pub fractal_type: FractalType,
    pub viewport: Viewport,
    pub max_iterations: u32,
    pub palette_type: PaletteType,
    pub palette_offset: f32,
    pub color_processor_type: crate::color_pipeline::ColorProcessorType,
    pub fractal_params: HashMap<String, f64>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            fractal_type: FractalType::Mandelbrot,
            viewport: Viewport::default(),
            max_iterations: 200,
            palette_type: PaletteType::Classic,
            palette_offset: 0.0,
            color_processor_type: crate::color_pipeline::ColorProcessorType::default(),
            fractal_params: HashMap::new(),
        }
    }
}

/// Trait for reversible commands
pub trait Command: Send + Sync {
    /// Execute the command, modifying the state
    fn execute(&self, state: &mut AppState);

    /// Undo the command, restoring previous state
    fn undo(&self, state: &mut AppState);

    /// Get a description of what this command does
    fn description(&self) -> String;

    /// Clone this command into a Box
    fn clone_box(&self) -> Box<dyn Command>;
}

impl Clone for Box<dyn Command> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}

/// Command for changing the view (pan/zoom)
#[derive(Debug, Clone)]
pub struct ViewCommand {
    old_viewport: Viewport,
    new_viewport: Viewport,
}

impl ViewCommand {
    pub fn new(old_viewport: Viewport, new_viewport: Viewport) -> Self {
        Self {
            old_viewport,
            new_viewport,
        }
    }
}

impl Command for ViewCommand {
    fn execute(&self, state: &mut AppState) {
        state.viewport = self.new_viewport;
    }

    fn undo(&self, state: &mut AppState) {
        state.viewport = self.old_viewport;
    }

    fn description(&self) -> String {
        let (old_center_x, old_center_y) = self.old_viewport.center();
        let (new_center_x, new_center_y) = self.new_viewport.center();
        let old_zoom = self.old_viewport.zoom();
        let new_zoom = self.new_viewport.zoom();

        if (old_zoom - new_zoom).abs() > 0.01 {
            format!("Zoom from {:.2} to {:.2}", old_zoom, new_zoom)
        } else {
            format!(
                "Pan from ({:.4}, {:.4}) to ({:.4}, {:.4})",
                old_center_x, old_center_y, new_center_x, new_center_y
            )
        }
    }

    fn clone_box(&self) -> Box<dyn Command> {
        Box::new(self.clone())
    }
}

/// Command for changing fractal parameters
#[derive(Debug, Clone)]
pub struct ParameterCommand {
    param_name: String,
    old_value: f64,
    new_value: f64,
}

impl ParameterCommand {
    pub fn new(param_name: String, old_value: f64, new_value: f64) -> Self {
        Self {
            param_name,
            old_value,
            new_value,
        }
    }
}

impl Command for ParameterCommand {
    fn execute(&self, state: &mut AppState) {
        state
            .fractal_params
            .insert(self.param_name.clone(), self.new_value);
    }

    fn undo(&self, state: &mut AppState) {
        state
            .fractal_params
            .insert(self.param_name.clone(), self.old_value);
    }

    fn description(&self) -> String {
        format!(
            "Set {} from {:.4} to {:.4}",
            self.param_name, self.old_value, self.new_value
        )
    }

    fn clone_box(&self) -> Box<dyn Command> {
        Box::new(self.clone())
    }
}

/// Command for changing the fractal type
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct FractalTypeCommand {
    old_type: FractalType,
    new_type: FractalType,
    old_params: HashMap<String, f64>,
    new_params: HashMap<String, f64>,
    old_viewport: Viewport,
    new_viewport: Viewport,
}

#[allow(dead_code)]
impl FractalTypeCommand {
    pub fn new(
        old_type: FractalType,
        new_type: FractalType,
        old_params: HashMap<String, f64>,
        new_params: HashMap<String, f64>,
        old_viewport: Viewport,
        new_viewport: Viewport,
    ) -> Self {
        Self {
            old_type,
            new_type,
            old_params,
            new_params,
            old_viewport,
            new_viewport,
        }
    }
}

impl Command for FractalTypeCommand {
    fn execute(&self, state: &mut AppState) {
        state.fractal_type = self.new_type;
        state.fractal_params = self.new_params.clone();
        state.viewport = self.new_viewport;
    }

    fn undo(&self, state: &mut AppState) {
        state.fractal_type = self.old_type;
        state.fractal_params = self.old_params.clone();
        state.viewport = self.old_viewport;
    }

    fn description(&self) -> String {
        format!("Switch from {:?} to {:?}", self.old_type, self.new_type)
    }

    fn clone_box(&self) -> Box<dyn Command> {
        Box::new(self.clone())
    }
}

/// Command for changing iteration count
#[derive(Debug, Clone)]
pub struct IterationCommand {
    old_iterations: u32,
    new_iterations: u32,
}

impl IterationCommand {
    pub fn new(old_iterations: u32, new_iterations: u32) -> Self {
        Self {
            old_iterations,
            new_iterations,
        }
    }
}

impl Command for IterationCommand {
    fn execute(&self, state: &mut AppState) {
        state.max_iterations = self.new_iterations;
    }

    fn undo(&self, state: &mut AppState) {
        state.max_iterations = self.old_iterations;
    }

    fn description(&self) -> String {
        format!(
            "Change iterations from {} to {}",
            self.old_iterations, self.new_iterations
        )
    }

    fn clone_box(&self) -> Box<dyn Command> {
        Box::new(self.clone())
    }
}

/// Command for changing palette
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct PaletteCommand {
    old_palette: PaletteType,
    new_palette: PaletteType,
    old_offset: f32,
    new_offset: f32,
}

#[allow(dead_code)]
impl PaletteCommand {
    pub fn new(
        old_palette: PaletteType,
        new_palette: PaletteType,
        old_offset: f32,
        new_offset: f32,
    ) -> Self {
        Self {
            old_palette,
            new_palette,
            old_offset,
            new_offset,
        }
    }
}

impl Command for PaletteCommand {
    fn execute(&self, state: &mut AppState) {
        state.palette_type = self.new_palette;
        state.palette_offset = self.new_offset;
    }

    fn undo(&self, state: &mut AppState) {
        state.palette_type = self.old_palette;
        state.palette_offset = self.old_offset;
    }

    fn description(&self) -> String {
        format!(
            "Change palette from {:?} to {:?}",
            self.old_palette, self.new_palette
        )
    }

    fn clone_box(&self) -> Box<dyn Command> {
        Box::new(self.clone())
    }
}

/// History manager for undo/redo
pub struct CommandHistory {
    commands: Vec<Box<dyn Command>>,
    current_index: usize,
    max_size: usize,
}

impl CommandHistory {
    pub fn new(max_size: usize) -> Self {
        Self {
            commands: Vec::new(),
            current_index: 0,
            max_size,
        }
    }

    /// Execute a command and add it to history
    pub fn execute(&mut self, command: Box<dyn Command>, state: &mut AppState) {
        // Remove any commands after current index (redo history)
        if self.current_index < self.commands.len() {
            self.commands.truncate(self.current_index);
        }

        // Execute the command
        command.execute(state);

        // Add to history
        self.commands.push(command);
        self.current_index += 1;

        // Limit history size
        if self.commands.len() > self.max_size {
            self.commands.remove(0);
            self.current_index -= 1;
        }
    }

    /// Undo the last command
    pub fn undo(&mut self, state: &mut AppState) -> Option<String> {
        if self.can_undo() {
            self.current_index -= 1;
            let command = &self.commands[self.current_index];
            command.undo(state);
            Some(command.description())
        } else {
            None
        }
    }

    /// Redo the next command
    pub fn redo(&mut self, state: &mut AppState) -> Option<String> {
        if self.can_redo() {
            let command = &self.commands[self.current_index];
            command.execute(state);
            self.current_index += 1;
            Some(command.description())
        } else {
            None
        }
    }

    /// Check if undo is available
    pub fn can_undo(&self) -> bool {
        self.current_index > 0
    }

    /// Check if redo is available
    pub fn can_redo(&self) -> bool {
        self.current_index < self.commands.len()
    }

    /// Get the number of commands in history
    #[allow(dead_code)]
    pub fn len(&self) -> usize {
        self.commands.len()
    }

    /// Check if history is empty
    #[allow(dead_code)]
    pub fn is_empty(&self) -> bool {
        self.commands.is_empty()
    }

    /// Get a description of the command that would be undone
    #[allow(dead_code)]
    pub fn undo_description(&self) -> Option<String> {
        if self.can_undo() {
            Some(self.commands[self.current_index - 1].description())
        } else {
            None
        }
    }

    /// Get a description of the command that would be redone
    #[allow(dead_code)]
    pub fn redo_description(&self) -> Option<String> {
        if self.can_redo() {
            Some(self.commands[self.current_index].description())
        } else {
            None
        }
    }

    /// Clear all history
    #[allow(dead_code)]
    pub fn clear(&mut self) {
        self.commands.clear();
        self.current_index = 0;
    }

    /// Get recent command descriptions for display
    #[allow(dead_code)]
    pub fn recent_descriptions(&self, count: usize) -> Vec<String> {
        let start = self.current_index.saturating_sub(count);
        self.commands[start..self.current_index]
            .iter()
            .map(|cmd| cmd.description())
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_view_command() {
        let old_viewport = Viewport::new(0.0, 0.0, 1.0);
        let new_viewport = Viewport::new(1.0, 1.0, 2.0);
        let cmd = ViewCommand::new(old_viewport, new_viewport);

        let mut state = AppState {
            viewport: old_viewport,
            ..Default::default()
        };

        cmd.execute(&mut state);
        assert_eq!(state.viewport.center(), (1.0, 1.0));
        assert_eq!(state.viewport.zoom(), 2.0);

        cmd.undo(&mut state);
        assert_eq!(state.viewport.center(), (0.0, 0.0));
        assert_eq!(state.viewport.zoom(), 1.0);
    }

    #[test]
    fn test_parameter_command() {
        let cmd = ParameterCommand::new("power".to_string(), 2.0, 3.0);

        let mut state = AppState::default();
        state.fractal_params.insert("power".to_string(), 2.0);

        cmd.execute(&mut state);
        assert_eq!(state.fractal_params.get("power"), Some(&3.0));

        cmd.undo(&mut state);
        assert_eq!(state.fractal_params.get("power"), Some(&2.0));
    }

    #[test]
    fn test_command_history() {
        let mut history = CommandHistory::new(10);
        let mut state = AppState::default();

        assert!(!history.can_undo());

        // Execute some commands
        let cmd1 = Box::new(ViewCommand::new(
            Viewport::default(),
            Viewport::new(1.0, 0.0, 1.0),
        ));
        history.execute(cmd1, &mut state);
        assert_eq!(state.viewport.center().0, 1.0);

        let cmd2 = Box::new(ViewCommand::new(
            Viewport::new(1.0, 0.0, 1.0),
            Viewport::new(2.0, 0.0, 1.0),
        ));
        history.execute(cmd2, &mut state);
        assert_eq!(state.viewport.center().0, 2.0);

        // Undo
        assert!(history.can_undo());
        history.undo(&mut state);
        assert_eq!(state.viewport.center().0, 1.0);

        // Redo
        assert!(history.can_redo());
        history.redo(&mut state);
        assert_eq!(state.viewport.center().0, 2.0);

        // Clear
        history.clear();
        assert!(!history.can_undo());
        assert!(!history.can_redo());
    }

    #[test]
    fn test_history_limit() {
        let mut history = CommandHistory::new(3);
        let mut state = AppState::default();

        // Add 5 commands (max is 3)
        for i in 0..5 {
            let cmd = Box::new(ViewCommand::new(
                Viewport::new(i as f64, 0.0, 1.0),
                Viewport::new((i + 1) as f64, 0.0, 1.0),
            ));
            history.execute(cmd, &mut state);
        }

        assert_eq!(history.len(), 3);

        // Should only be able to undo 3 times
        assert!(history.undo(&mut state).is_some());
        assert!(history.undo(&mut state).is_some());
        assert!(history.undo(&mut state).is_some());
        assert!(history.undo(&mut state).is_none()); // Nothing left to undo
    }

    #[test]
    fn test_undo_clears_redo() {
        let mut history = CommandHistory::new(10);
        let mut state = AppState::default();

        // Add 3 commands
        for i in 0..3 {
            let cmd = Box::new(ViewCommand::new(
                Viewport::new(i as f64, 0.0, 1.0),
                Viewport::new((i + 1) as f64, 0.0, 1.0),
            ));
            history.execute(cmd, &mut state);
        }

        // Undo one
        history.undo(&mut state);
        assert!(history.can_redo());

        // Add a new command (should clear redo history)
        let cmd = Box::new(ViewCommand::new(
            Viewport::new(2.0, 0.0, 1.0),
            Viewport::new(10.0, 0.0, 1.0),
        ));
        history.execute(cmd, &mut state);

        assert!(!history.can_redo());
        assert_eq!(history.len(), 3); // Still 3, not 4
    }

    #[test]
    fn test_command_descriptions() {
        let cmd = ViewCommand::new(Viewport::new(0.0, 0.0, 1.0), Viewport::new(1.0, 2.0, 1.0));
        assert!(cmd.description().contains("Pan"));

        let zoom_cmd = ViewCommand::new(Viewport::new(0.0, 0.0, 1.0), Viewport::new(0.0, 0.0, 2.0));
        assert!(zoom_cmd.description().contains("Zoom"));

        let param_cmd = ParameterCommand::new("power".to_string(), 2.0, 3.0);
        assert!(param_cmd.description().contains("power"));

        let iter_cmd = IterationCommand::new(100, 200);
        assert!(iter_cmd.description().contains("200"));
    }
}
