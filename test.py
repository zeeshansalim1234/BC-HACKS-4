from google.cloud import language_v1
def sample_classify_text(text_content):
    """
    Classifying Content in a String

    Args:
      text_content The text content to analyze.
    """

    client = language_v1.LanguageServiceClient()

    # text_content = "That actor on TV makes movies in Hollywood and also stars in a variety of popular new TV shows."

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    content_categories_version = (
        language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2)
    response = client.classify_text(request = {
        "document": document,
        "classification_model_options": {
            "v2_model": {
                "content_categories_version": content_categories_version
            }
        }
    })
    
    category = response.categories[0].name

sample_classify_text("Pre-trained word embeddings like ELMo and BERT contain rich syntactic and semantic information, resulting in state-of-the-art performance on various tasks. We propose a very fast variational information bottleneck (VIB) method to nonlinearly compress these embeddings, keeping only the information that helps a discriminative parser. We compress each word embedding to either a discrete tag or a continuous vector. In the discrete version, our automatically compressed tags form an alternative tag set: we show experimentally that our tags capture most of the information in traditional POS tag annotations, but our tag sequences can be parsed more accurately at the same level of tag granularity. In the continuous version, we show experimentally that moderately compressing the word embeddings by our method yields a more accurate parser in 8 of 9 languages, unlike simple dimensionality reduction.")