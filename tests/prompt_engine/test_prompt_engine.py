"""Comprehensive unit test suite for Module 06: Prompt Engine."""

import os
import shutil
import unittest
from src.prompt_engine import (
    PromptEngine,
    PromptBuilder,
    PromptTemplate,
    TemplateVariable,
    ValidationError,
    TemplateNotFoundError,
    RenderError,
)


class TestPromptEngine(unittest.TestCase):
    """Verifies all components and pipelines of the Enterprise Prompt Engine."""

    def setUp(self) -> None:
        """Sets up isolated, clean workspace directories for repository testing."""
        self.test_dir = "./test_assets_prompts"
        self.test_history = "./test_assets_prompt_history.jsonl"
        
        # Clean potential leftovers
        self.tearDown()

        # Initialize engine
        self.engine = PromptEngine(
            storage_dir=self.test_dir,
            history_filepath=self.test_history,
        )

    def tearDown(self) -> None:
        """Cleans up temporary asset and log files generated during unit execution."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.test_history):
            try:
                os.remove(self.test_history)
            except OSError:
                pass

    def test_programmatic_builder_and_validation(self) -> None:
        """Ensures PromptBuilder constructs a clean PromptTemplate and triggers validation constraints."""
        builder = (
            PromptBuilder("coffee_promo")
            .set_category("Marketing")
            .set_provider("Gemini")
            .set_description("Organic coffee promo template")
            .set_system_prompt("You are a coffee guru.")
            .set_user_prompt("Write about {{ coffee_blend }} in Vietnam.")
            .add_variable(
                name="coffee_blend",
                description="The coffee blend name",
                default_value="Robust Arabica",
                is_required=True,
                type_hint="str",
            )
        )
        template = builder.build()

        self.assertEqual(template.name, "coffee_promo")
        self.assertEqual(template.provider, "Gemini")
        self.assertEqual(template.category, "Marketing")
        self.assertEqual(len(template.variables), 1)
        self.assertEqual(template.variables[0].name, "coffee_blend")

        # Verify validation error for invalid variable names
        with self.assertRaises(ValidationError):
            bad_builder = PromptBuilder("invalid_var").add_variable(name="bad-name!").build()
            self.engine.create_template(bad_builder)

    def test_rendering_and_variable_resolution(self) -> None:
        """Tests rendering pipeline including type casting and fallbacks."""
        builder = (
            PromptBuilder("calc_template")
            .set_category("Marketing")
            .set_provider("OpenAI")
            .set_user_prompt("The total quantity is {{ item_count }} items. Price: {{ price }}.")
            .add_variable(name="item_count", type_hint="int", is_required=True)
            .add_variable(name="price", type_hint="float", default_value=1.99, is_required=False)
        )
        template = builder.build()
        self.engine.create_template(template)

        # Test valid rendering with string-to-int type-casting
        rendered = self.engine.render_prompt(
            "calc_template",
            user_variables={"item_count": "42"},  # passed as string, should cast to int
        )

        self.assertEqual(rendered.user_prompt, "The total quantity is 42 items. Price: 1.99.")
        self.assertEqual(rendered.resolved_variables["item_count"], 42)
        self.assertEqual(rendered.resolved_variables["price"], 1.99)
        self.assertEqual(len(rendered.unresolved_variables), 0)

    def test_version_bumping_and_comparison(self) -> None:
        """Verifies version increments, history logging, and visual comparing."""
        builder = (
            PromptBuilder("versioned_template")
            .set_category("SEO")
            .set_provider("Gemini")
            .set_user_prompt("Original content: {{ content }}")
        )
        template = builder.build()
        self.engine.create_template(template)

        # Increment version: 1.0.0 -> 1.0.1
        new_tpl = self.engine.version_bump(
            template_name="versioned_template",
            new_user_prompt="Enhanced content: {{ content }}",
            bump_type="patch",
            change_description="Upgraded structure",
        )

        self.assertEqual(new_tpl.version, "1.0.1")
        self.assertEqual(len(new_tpl.version_history), 1)

        # Compare version 1.0.0 and 1.0.1
        compare_result = self.engine.compare_templates("versioned_template", "1.0.0", "1.0.1")
        
        # Check that there are lines added and deleted
        self.assertTrue(any(line.type == "delete" for line in compare_result.user_prompt_diff))
        self.assertTrue(any(line.type == "insert" for line in compare_result.user_prompt_diff))

    def test_token_optimization(self) -> None:
        """Verifies whitespaces compression and polite filler words removal."""
        raw_text = "   Hello!  Can you please write a script?   Thank you so much.   "
        optimized = self.engine.optimize_prompt(
            raw_text, compress_whitespace=True, remove_fillers=True
        )

        self.assertIn("Hello!", optimized.optimized_text)
        self.assertNotIn("please", optimized.optimized_text)
        self.assertNotIn("Thank you", optimized.optimized_text)
        self.assertTrue(optimized.original_characters > optimized.optimized_characters)
        self.assertTrue(optimized.tokens_saved_estimate >= 1)

    def test_split_ab_testing(self) -> None:
        """Tests ratio-based split evaluation routing and conversion logging."""
        config = self.engine.create_ab_test(
            test_id="test_opt_ratio",
            name="Split Test 1",
            template_name="test_tpl",
            version_a="1.0.0",
            version_b="1.1.0",
            allocation_ratio_a=0.5,
        )

        # Run multiple selections
        selections = [self.engine.select_test_version(config)[1] for _ in range(100)]
        
        self.assertIn("A", selections)
        self.assertIn("B", selections)

        # Record conversion
        self.engine.record_test_conversion(config, "A")
        stats = self.engine.get_test_stats(config)

        self.assertEqual(stats["variant_a"]["conversions"], 1)

    def test_export_import_serialization(self) -> None:
        """Verifies formatting template configs into JSON/YAML and loading them back."""
        builder = (
            PromptBuilder("export_template")
            .set_category("Translation")
            .set_provider("Claude")
            .set_user_prompt("Translate {{ text }} to French.")
        )
        template = builder.build()

        # JSON Export/Import
        json_str = self.engine.export_to_json(template)
        imported_json = self.engine.import_from_json(json_str)
        self.assertEqual(imported_json.name, "export_template")
        self.assertEqual(imported_json.provider, "Claude")

        # YAML Export/Import
        yaml_str = self.engine.export_to_yaml(template)
        imported_yaml = self.engine.import_from_yaml(yaml_str)
        self.assertEqual(imported_yaml.name, "export_template")
        self.assertEqual(imported_yaml.provider, "Claude")

    def test_execution_diagnostics_and_conversion_recording(self) -> None:
        """Verifies history tracking, diagnostics, and conversion markers."""
        builder = (
            PromptBuilder("diagnostics_template")
            .set_category("SEO")
            .set_provider("Gemini")
            .set_user_prompt("SEO prompt {{ keyword }}")
            .add_variable(name="keyword")
        )
        self.engine.create_template(builder.build())

        # Render
        self.engine.render_prompt("diagnostics_template", {"keyword": "Coffee Roasted"})
        
        # Verify history file has record
        history = self.engine.get_history("diagnostics_template")
        self.assertEqual(len(history), 1)
        record = history[0]
        self.assertEqual(record.variables_used["keyword"], "Coffee Roasted")
        self.assertFalse(record.conversion_recorded)

        # Mark conversion
        success = self.engine.mark_conversion(record.id)
        self.assertTrue(success)

        # Load again to check conversion flag
        updated_history = self.engine.get_history("diagnostics_template")
        self.assertTrue(updated_history[0].conversion_recorded)


if __name__ == "__main__":
    unittest.main()
