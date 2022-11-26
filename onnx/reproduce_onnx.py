import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from transformers import BertConfig, BertTokenizerFast, FeatureExtractionPipeline
from transformers.convert_graph_to_onnx import (
    convert,
    ensure_valid_input,
    generate_identified_filename,
    infer_shapes,
    quantize,
)
from transformers.testing_utils import require_tf, require_tokenizers, require_torch, slow


class FuncContiguousArgs:
    def forward(self, input_ids, token_type_ids, attention_mask):
        return None


class FuncNonContiguousArgs:
    def forward(self, input_ids, some_other_args, token_type_ids, attention_mask):
        return None


class OnnxExportTestCase(unittest.TestCase):
    MODEL_TO_TEST = [
        # (model_name, model_kwargs)
        ("bert-base-cased", {}),
        ("gpt2", {"use_cache": False}),  # We don't support exporting GPT2 past keys anymore
    ]

    @require_tf
    @slow
    def test_export_tensorflow(self):
        for model, model_kwargs in OnnxExportTestCase.MODEL_TO_TEST:
            self._test_export(model, "tf", 12, **model_kwargs)

    @require_torch
    @slow
    def test_export_pytorch(self):
        for model, model_kwargs in OnnxExportTestCase.MODEL_TO_TEST:
            self._test_export(model, "pt", 12, **model_kwargs)

    @require_torch
    @slow
    def test_export_custom_bert_model(self):
        from transformers import BertModel

        with NamedTemporaryFile(mode="w+t") as vocab_file:
            vocab_file.write("\n".join(vocab))
            vocab_file.flush()
            tokenizer = BertTokenizerFast(vocab_file.name)

        with TemporaryDirectory() as bert_save_dir:
            model = BertModel(BertConfig(vocab_size=len(vocab)))
            model.save_pretrained(bert_save_dir)
            self._test_export(bert_save_dir, "pt", 12, tokenizer)

    @require_tf
    @slow
    def test_quantize_tf(self):
        for model, model_kwargs in OnnxExportTestCase.MODEL_TO_TEST:
            path = self._test_export(model, "tf", 12, **model_kwargs)
            quantized_path = quantize(Path(path))

    @require_torch
    @slow
    def test_quantize_pytorch(self):
        for model, model_kwargs in OnnxExportTestCase.MODEL_TO_TEST:
            path = self._test_export(model, "pt", 12, **model_kwargs)
            quantized_path = quantize(path)

    def _test_export(self, model, framework, opset, tokenizer=None, **model_kwargs):
        try:
            # Compute path
            with TemporaryDirectory() as tempdir:
                path = Path(tempdir).joinpath("model.onnx")
            # Remove folder if exists
            if path.parent.exists():
                path.parent.rmdir()
            # Export
            convert(framework, model, path, opset, tokenizer, **model_kwargs)
            return path
        except Exception as e:
            self.fail(e)

    def test_generate_identified_name(self):
        generated = generate_identified_filename(Path("/gcp/training/export/export.json"), "-test")
        self.assertEqual("/gcp/training/export/test_export.json", generated.as_posix())