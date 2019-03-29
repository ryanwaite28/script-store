const ArrayPaginator = function ArrayPaginator(arrayObject) {
  const self = this;

  let copyArrayObject = arrayObject.slice(0);
  let startIndex = 0;
  let sectionSize = 10;
  let page = 1;
  let pages = copyArrayObject.length / sectionSize;
  let currentSection = copyArrayObject.slice(startIndex, (startIndex + sectionSize));
  let filterFn;
  let sortFn;

  self.getCurrentSection = function() {
    return copyArrayObject.slice(startIndex, (startIndex + sectionSize));
  }

  self.getState = function() {
    return {
      startIndex: startIndex,
      sectionSize: sectionSize,
      page: page,
      pages: pages,
      currentSection: currentSection
    };
  }

  self.setDefaultSettings = function() {
    startIndex = 0;
    sectionSize = 10;
    page = 1;
    pages = arrayObject.length / sectionSize;
  }

  self.setSize = function(size) {
    sectionSize = size;
    startIndex = 0;
    page = 1;
    pages = arrayObject.length / sectionSize;
    currentSection = self.getCurrentSection();
  }

  self.setPage = function(pageNumber) {
    page = pageNumber;
    startIndex = (pageNumber * sectionSize) - sectionSize;
    currentSection = self.getCurrentSection();
  }

  self.setPrev = function() {
    if(page === 1) { return; }
    page = page - 1;
    startIndex = startIndex - sectionSize;
    currentSection = self.getCurrentSection();
  }

  self.setNext = function() {
    if(page === pages) { return; }
    page = page - 1;
    startIndex = startIndex - sectionSize;
    currentSection = self.getCurrentSection();
  }

  self.setFilterFn = function(callbackFn, launch) {
    filterFn = callbackFn;
    if (launch === true) {
      copyArrayObject = arrayObject.filter(filterFn);
      self.setDefaultSettings();
      currentSection = self.getCurrentSection();
    }
  }

  self.setSortFn = function(callbackFn, launch) {
    sortFn = callbackFn;
    if (launch === true) {
      copyArrayObject.sort(filterFn);
      currentSection = self.getCurrentSection();
    }
  }

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
  }

  self.applySort = function(callbackFn) {
    if (callbackFn) {
      copyArrayObject.sort(callbackFn);
      currentSection = self.getCurrentSection();
    } else if (sortFn) {
      copyArrayObject.sort(sortFn);
      currentSection = self.getCurrentSection();
    }
  }

  self.clearFilter = function(callbackFn) {
    filterFn = null;
    copyArrayObject = arrayObject.slice(0);
  }

  self.clearSort = function(callbackFn) {
    sortFn = null;
    copyArrayObject = arrayObject.slice(0);
  }
}