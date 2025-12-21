"""
Test for CodeTransformer service
"""
import pytest
from app.services.code_transformer import CodeTransformer


@pytest.mark.asyncio
async def test_code_transformer_initialization():
    """Test that CodeTransformer can be initialized"""
    transformer = CodeTransformer()
    assert transformer is not None
    assert transformer.transformations_applied == []


def test_language_from_extension():
    """Test language detection from file extension"""
    transformer = CodeTransformer()
    
    assert transformer._get_language_from_extension('.py') == 'Python'
    assert transformer._get_language_from_extension('.js') == 'JavaScript'
    assert transformer._get_language_from_extension('.ts') == 'TypeScript'
    assert transformer._get_language_from_extension('.java') == 'Java'
    assert transformer._get_language_from_extension('.go') == 'Go'
    assert transformer._get_language_from_extension('.rs') == 'Rust'


def test_python_transformation():
    """Test Python code transformation"""
    transformer = CodeTransformer()
    
    # Test old-style exception handling
    old_code = """
try:
    something()
except Exception, e:
    print e
"""
    
    transformed, changes = transformer._transform_python(old_code)
    assert 'except Exception as e:' in transformed
    assert len(changes) > 0


def test_javascript_transformation():
    """Test JavaScript code transformation"""
    transformer = CodeTransformer()
    
    # Test var detection
    old_code = """
var x = 10;
var y = 20;
"""
    
    transformed, changes = transformer._transform_javascript(old_code)
    assert len(changes) > 0
    assert any('var' in change.lower() for change in changes)


def test_java_transformation():
    """Test Java code transformation"""
    transformer = CodeTransformer()
    
    code = """
public class Test {
    private String name;
    private int age;
}
"""
    
    transformed, changes = transformer._transform_java(code)
    assert len(changes) > 0


def test_go_transformation():
    """Test Go code transformation"""
    transformer = CodeTransformer()
    
    code = """
func process(data interface{}) error {
    return nil
}
"""
    
    transformed, changes = transformer._transform_go(code)
    assert len(changes) > 0
    assert any('generics' in change.lower() for change in changes)


def test_rust_transformation():
    """Test Rust code transformation"""
    transformer = CodeTransformer()
    
    code = """
fn process() -> Result<String, Error> {
    let value = something().unwrap();
    Ok(value)
}
"""
    
    transformed, changes = transformer._transform_rust(code)
    assert len(changes) > 0
    assert any('unwrap' in change.lower() for change in changes)
