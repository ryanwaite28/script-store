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

export interface ArrayPaginatorState {
  startIndex: number;
  startNum: number;
  endIndex: number;
  endNum: number;
  sectionSize: number;
  page: number;
  pages: number;
  pageNumbers: number[];
  currentSection: Array<any>;
  copyArrayObject: Array<any>;
  totalSize: number;
}

export class ArrayPaginator {
  // private properties
  private arrayObject;

  private copyArrayObject;
  private sectionSize;
  private startIndex;
  private endIndex;
  private page;
  private pages;
  private currentSection;
  private filterFn;
  private sortFn;

  constructor(
    arrayObject: Array<any>,
    initSize: number = 20
  ) {
    this.init(arrayObject, initSize);
  }

  private init(
    arrayObject: Array<any>,
    initSize: number = 20
  ) {
    if (!arrayObject) {
      return;
    }

    this.arrayObject = arrayObject;

    this.copyArrayObject = arrayObject.slice(0);
    this.sectionSize = initSize;
    this.startIndex = 0;
    this.endIndex = this.startIndex + (this.sectionSize - 1);
    this.page = 1;
    this.pages = Math.ceil(this.copyArrayObject.length / this.sectionSize);
    this.currentSection = this.copyArrayObject.slice(this.startIndex, (this.startIndex + this.sectionSize));
  }

  setList(arrayObject: Array<any>) {
    this.init(arrayObject, this.sectionSize);
  }

  getCurrentSection(): Array<any> {
    return this.copyArrayObject.slice(this.startIndex, (this.startIndex + this.sectionSize));
  }

  getList(): Array<any> {
    return this.copyArrayObject.slice(0);
  }

  getState(): ArrayPaginatorState {
    return {
      startIndex: this.startIndex,
      startNum: this.startIndex + 1,
      endIndex: this.endIndex,
      endNum: this.endIndex > this.copyArrayObject.length ? this.copyArrayObject.length : (this.endIndex + 1),
      sectionSize: this.sectionSize,
      page: this.page,
      pages: this.pages,
      pageNumbers: Array(this.pages).fill(0).map((v, i) => i + 1),
      currentSection: this.currentSection,
      copyArrayObject: this.copyArrayObject,
      totalSize: this.copyArrayObject.length,
    };
  }

  setDefaultSettings() {
    this.startIndex = 0;
    this.endIndex = this.startIndex + (this.sectionSize - 1);
    this.sectionSize = 10;
    this.page = 1;
    this.pages = Math.ceil(this.copyArrayObject.length / this.sectionSize);
    return true;
  }

  setSize(size) {
    this.sectionSize = size;
    this.startIndex = 0;
    this.endIndex = this.startIndex + (this.sectionSize - 1);
    this.page = 1;
    this.pages = Math.ceil(this.copyArrayObject.length / this.sectionSize);
    this.currentSection = this.getCurrentSection();
    return true;
  }

  isWithinRange(pageNumber) {
    const numberValue = Math.abs(pageNumber);
    if (isNaN(numberValue)) {
      return false;
    }
    const invalidNumber = numberValue === Infinity;
    const outOfRange = numberValue > this.pages || numberValue < 1;
    const isValidNumber = !outOfRange && !invalidNumber;
    return isValidNumber;
  }

  setPage(pageNumber) {
    const results = this.isWithinRange(pageNumber);
    if (!results) {
      // 'number not within range:', results, pageNumber, this
      return false;
    }
    this.page = pageNumber;
    this.startIndex = (pageNumber * this.sectionSize) - this.sectionSize;
    this.endIndex = this.startIndex + (this.sectionSize - 1);
    this.currentSection = this.getCurrentSection();
    return true;
  }

  setPrev() {
    if (this.page === 1) { return; }
    this.page = this.page - 1;
    this.startIndex = this.startIndex - this.sectionSize;
    this.endIndex = this.startIndex + (this.sectionSize - 1);
    this.currentSection = this.getCurrentSection();
    return true;
  }

  setNext() {
    if (this.page === this.pages) { return; }
    this.page = this.page + 1;
    this.startIndex = this.startIndex + this.sectionSize;
    this.endIndex = this.startIndex + (this.sectionSize - 1);
    this.currentSection = this.getCurrentSection();
    return true;
  }

  setFilterFn(callbackFn, launch) {
    this.filterFn = callbackFn;
    if (launch === true) {
      this.copyArrayObject = this.arrayObject.filter(this.filterFn);
      this.setDefaultSettings();
      this.currentSection = this.getCurrentSection();
    }
    return true;
  }

  setSortFn(callbackFn, launch) {
    this.sortFn = callbackFn;
    if (launch === true) {
      this.copyArrayObject.sort(this.filterFn);
      this.currentSection = this.getCurrentSection();
    }
    return true;
  }

  applyFilter(callbackFn) {
    if (callbackFn) {
      this.copyArrayObject = this.arrayObject.filter(callbackFn);
      this.setDefaultSettings();
      this.currentSection = this.getCurrentSection();
    } else if (this.filterFn) {
      this.copyArrayObject = this.arrayObject.filter(this.filterFn);
      this.setDefaultSettings();
      this.currentSection = this.getCurrentSection();
    }
    return true;
  }

  applySort(callbackFn) {
    if (callbackFn) {
      this.copyArrayObject.sort(callbackFn);
      this.currentSection = this.getCurrentSection();
    } else if (this.sortFn) {
      this.copyArrayObject.sort(this.sortFn);
      this.currentSection = this.getCurrentSection();
    }
    return true;
  }

  clearFilter() {
    this.filterFn = null;
    this.copyArrayObject = this.arrayObject.slice(0);
    return true;
  }

  clearSort() {
    this.sortFn = null;
    this.copyArrayObject = this.arrayObject.slice(0);
    return true;
  }
}
