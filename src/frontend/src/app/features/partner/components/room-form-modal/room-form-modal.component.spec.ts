import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoomFormModalComponent } from './room-form-modal.component';

describe('RoomFormModalComponent', () => {
  let component: RoomFormModalComponent;
  let fixture: ComponentFixture<RoomFormModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoomFormModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoomFormModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
