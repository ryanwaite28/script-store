/**
 * Array Paginator
 * ---
 * Constructor for managing large lists of data.
 * @example
 * - const paginator = new ArrayPaginator([ ... ]);
 * @end
 *
 * One thing to note is the `return true;` statements at the end of most methods.
 * This is to let the caller know that the operation was successful.
 *
 * @param arrayObject Array object
 * @return {ArrayPaginator} new instance of `ArrayPaginator`
 */
export function ArrayPaginator(
  arrayObject,
  initSize: 20
) {
  const self = this;

  let copyArrayObject = [ ...arrayObject ];
  let sectionSize = initSize;
  let startIndex = 0;
  let endIndex = startIndex + (sectionSize - 1);
  let page = 1;
  let pages = Math.ceil(copyArrayObject.length / sectionSize);
  let currentSection = copyArrayObject.slice(startIndex, (startIndex + sectionSize));
  let filterFn;
  let sortFn;

  self.getCurrentSection = function() {
    return copyArrayObject.slice(startIndex, (startIndex + sectionSize));
  };

  self.getState = function() {
    return {
      startIndex,
      startNum: startIndex + 1,
      endIndex,
      endNum: endIndex > copyArrayObject.length ? copyArrayObject.length : (endIndex + 1),
      sectionSize,
      page,
      pages,
      currentSection,
      copyArrayObject,
    };
  };

  self.setDefaultSettings = function() {
    startIndex = 0;
    endIndex = startIndex + (sectionSize - 1);
    sectionSize = 10;
    page = 1;
    pages = Math.ceil(copyArrayObject.length / sectionSize);
    return true;
  };

  self.setSize = function(size) {
    sectionSize = size;
    startIndex = 0;
    endIndex = startIndex + (sectionSize - 1);
    page = 1;
    pages = Math.ceil(copyArrayObject.length / sectionSize);
    currentSection = self.getCurrentSection();
    return true;
  };

  self.isWithinRange = function(pageNumber) {
    if (isNaN(pageNumber)) {
      return false;
    }
    const numberValue = Math.abs(pageNumber);
    const invalidNumber = numberValue === Infinity;
    const outOfRange = numberValue > pages || numberValue < 1;

    const isValidNumber = !outOfRange && !invalidNumber;
    return isValidNumber;
  };

  self.setPage = function(pageNumber) {
    const results = self.isWithinRange(pageNumber);
    if (!results) {
      console.warn('number not within range:', pageNumber);
      return false;
    }
    page = pageNumber;
    startIndex = (pageNumber * sectionSize) - sectionSize;
    endIndex = startIndex + (sectionSize - 1);
    currentSection = self.getCurrentSection();
    return true;
  };

  self.setPrev = function() {
    if (page === 1) { return; }
    page = page - 1;
    startIndex = startIndex - sectionSize;
    endIndex = startIndex + (sectionSize - 1);
    currentSection = self.getCurrentSection();
    return true;
  };

  self.setNext = function() {
    if (page === pages) { return; }
    page = page + 1;
    startIndex = startIndex + sectionSize;
    endIndex = startIndex + (sectionSize - 1);
    currentSection = self.getCurrentSection();
    return true;
  };

  self.setFilterFn = function(callbackFn, launch) {
    filterFn = callbackFn;
    if (launch === true) {
      copyArrayObject = arrayObject.filter(filterFn);
      self.setDefaultSettings();
      currentSection = self.getCurrentSection();
    }
    return true;
  };

  self.setSortFn = function(callbackFn, launch) {
    sortFn = callbackFn;
    if (launch === true) {
      copyArrayObject.sort(filterFn);
      currentSection = self.getCurrentSection();
    }
    return true;
  };

  self.applyFilter = function(callbackFn) {
    if (callbackFn) {
      copyArrayObject = arrayObject.filter(callbackFn);
      self.setDefaultSettings();
      currentSection = self.getCurrentSection();
    } else if (filterFn) {
      copyArrayObject = arrayObject.filter(filterFn);
      self.setDefaultSettings();
      currentSection = self.getCurrentSection();
    }
    return true;
  };

  self.applySort = function(callbackFn) {
    if (callbackFn) {
      copyArrayObject.sort(callbackFn);
      currentSection = self.getCurrentSection();
    } else if (sortFn) {
      copyArrayObject.sort(sortFn);
      currentSection = self.getCurrentSection();
    }
    return true;
  };

  self.clearFilter = function(callbackFn) {
    filterFn = null;
    copyArrayObject = arrayObject.slice(0);
    return true;
  };

  self.clearSort = function(callbackFn) {
    sortFn = null;
    copyArrayObject = arrayObject.slice(0);
    return true;
  };
}
