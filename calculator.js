const OPERATOR_ADD                   = "OPERATOR_ADD";
const OPERATOR_SUBTRACT              = "OPERATOR_SUBTRACT";
const OPERATOR_MULTIPLY              = "OPERATOR_PLUS";
const OPERATOR_DIVIDE                = "OPERATOR_DIVIDE";
const OPERATOR_MODULO                = "OPERATOR_MODULO";

const OPERATOR_EVAL                  = "OPERATOR_EVAL";

const calc = function(values = [], operator = "") {
  // Checking operator
  if(operator.length === 0) { return null; }
  if(typeof(operator) !== 'string') {
    return null;
  }

  // Checking values
  if(values.length < 2) { return }
  for(let value of values) {
    if(typeof(value) !== 'number') {
      break;
      return null;
    }
  }

  switch(operator) {
    case OPERATOR_ADD:
      let value = values.reduce((acc, curr) => { return acc + curr });
      return value;

    case OPERATOR_SUBTRACT:
      let value = values.reduce((acc, curr) => { return acc - curr });
      return value;

    case OPERATOR_MULTIPLY:
      let value = values.reduce((acc, curr) => { return acc * curr });
      return value;

    case OPERATOR_DIVIDE:
      let value = values.reduce((acc, curr) => { return acc / curr });
      return value;

    case OPERATOR_MODULO:
      let value = values.reduce((acc, curr) => { return acc % curr });
      return value;

    default:
      return null;
  }

}

const eval_exp = function(expression) {
  if(expression.length === 0) { return }
  if(typeof(expression) !== 'string') { return }

  let value = eval(expression);
  return value;
}
